"""
insight_service.py
──────────────────
Business logic for AI-generated expense insights.

Flow:
  get_insights()
      ↳ check insight_cache (1-hour TTL)
          hit  → return InsightResponse(cached=True)
          miss → _generate_insights()
                     ↳ OpenAI gpt-4o-mini
                         ok  → upsert cache, return InsightResponse(cached=False)
                         fail→ Anthropic claude-haiku-4-5
                                   ok  → upsert cache, return InsightResponse(cached=False)
                                   fail→ return InsightError(error="AI temporarily unavailable")

  regenerate_insights()
      ↳ delete cache row → _generate_insights()

Privacy: only aggregated stats (totals, category sums, day-of-week breakdown)
         are ever sent to the LLM — never raw descriptions.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

import anthropic
import openai
from sqlalchemy import delete, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.category import Category
from app.models.expense import Expense
from app.models.insight_cache import InsightCache
from app.schemas.insight import InsightError, InsightResponse

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────
CACHE_TTL_HOURS = 1
OPENAI_MODEL = "gpt-4o-mini"
ANTHROPIC_MODEL = "claude-haiku-4-5"

SYSTEM_PROMPT = (
    "You are a personal finance analyst. Given monthly expense statistics, "
    "return ONLY a JSON object with this exact shape:\n"
    '{"insights": [3-5 strings], "anomalies": [1-3 strings], '
    '"suggestions": [2-4 strings], "confidence": float 0-1}\n'
    "Be specific and data-driven. No preamble, no markdown, no explanation outside the JSON."
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _prev_month(month: int, year: int) -> tuple[int, int]:
    """Return (month, year) for the month before the given one."""
    if month == 1:
        return 12, year - 1
    return month - 1, year


async def _build_stats(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> dict:
    """
    Build an aggregated statistics dictionary from the DB.
    No raw text — only numeric/categorical aggregates.
    """
    prev_month, prev_year = _prev_month(month, year)

    # 1. total_spent for current month
    total_spent_res = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
    )
    total_spent = float(total_spent_res.scalar_one())

    # 2. category_totals: {category_name: amount} for current month
    cat_res = await db.execute(
        select(
            Category.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
        .group_by(Category.name)
    )
    category_totals: dict[str, float] = {
        row.name: float(row.total) for row in cat_res.all()
    }

    # 3. prev_month_totals: same shape for previous month
    prev_cat_res = await db.execute(
        select(
            Category.name,
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == prev_month,
            extract("year", Expense.date) == prev_year,
        )
        .group_by(Category.name)
    )
    prev_month_totals: dict[str, float] = {
        row.name: float(row.total) for row in prev_cat_res.all()
    }

    # 4. day_of_week_breakdown: {0-6: total} for current month
    #    SQLAlchemy func.strftime for SQLite; also works on MySQL via func.dayofweek
    #    We use Python-side aggregation to stay DB-agnostic.
    date_res = await db.execute(
        select(Expense.date, Expense.amount).where(
            Expense.user_id == user_id,
            extract("month", Expense.date) == month,
            extract("year", Expense.date) == year,
        )
    )
    dow_breakdown: dict[int, float] = {i: 0.0 for i in range(7)}
    for row in date_res.all():
        dow_breakdown[row.date.weekday()] += float(row.amount)
    dow_breakdown = {k: round(v, 2) for k, v in dow_breakdown.items()}

    return {
        "month": month,
        "year": year,
        "total_spent": round(total_spent, 2),
        "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
        "prev_month_totals": {k: round(v, 2) for k, v in prev_month_totals.items()},
        "day_of_week_breakdown": dow_breakdown,
    }


def _parse_llm_json(raw: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first and last fence lines
        text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
    return json.loads(text)


def _build_insight_response(data: dict, cached: bool) -> InsightResponse:
    return InsightResponse(
        insights=data.get("insights", []),
        anomalies=data.get("anomalies", []),
        suggestions=data.get("suggestions", []),
        confidence=float(data.get("confidence", 0.0)),
        generated_at=datetime.now(timezone.utc),
        cached=cached,
    )


async def _upsert_cache(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
    response: InsightResponse,
) -> None:
    """Delete any existing cache row and insert the new one."""
    await db.execute(
        delete(InsightCache).where(
            InsightCache.user_id == user_id,
            InsightCache.month == month,
            InsightCache.year == year,
        )
    )
    payload = {
        "insights": response.insights,
        "anomalies": response.anomalies,
        "suggestions": response.suggestions,
        "confidence": response.confidence,
    }
    cache_row = InsightCache(
        user_id=user_id,
        month=month,
        year=year,
        insights_json=json.dumps(payload),
        generated_at=response.generated_at.replace(tzinfo=None),  # store naive UTC
    )
    db.add(cache_row)
    await db.commit()


# ── Core generation ────────────────────────────────────────────────────────────

async def _generate_insights(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> InsightResponse | InsightError:
    """
    Call LLM to generate insights from aggregated stats.
    Tries OpenAI first, falls back to Anthropic, then returns InsightError.
    """
    stats = await _build_stats(db, user_id, month, year)
    user_message = (
        f"Here are the expense statistics for {month}/{year}:\n"
        + json.dumps(stats, indent=2)
    )

    # ── Attempt 1: OpenAI ──────────────────────────────────────────────────────
    try:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        completion = await client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        raw = completion.choices[0].message.content or "{}"
        data = _parse_llm_json(raw)
        response = _build_insight_response(data, cached=False)
        await _upsert_cache(db, user_id, month, year, response)
        return response

    except Exception as exc:  # noqa: BLE001
        logger.warning("OpenAI call failed: %s — trying Anthropic fallback", exc)

    # ── Attempt 2: Anthropic ───────────────────────────────────────────────────
    try:
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        aclient = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = await aclient.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = message.content[0].text if message.content else "{}"
        data = _parse_llm_json(raw)
        response = _build_insight_response(data, cached=False)
        await _upsert_cache(db, user_id, month, year, response)
        return response

    except Exception as exc:  # noqa: BLE001
        logger.error("Anthropic fallback also failed: %s", exc)

    # ── Both failed ────────────────────────────────────────────────────────────
    return InsightError(error="AI temporarily unavailable")


# ── Public API ─────────────────────────────────────────────────────────────────

async def get_insights(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> InsightResponse | InsightError:
    """
    Return insights for the given user/month/year.
    Serves from cache when the cached row is less than CACHE_TTL_HOURS old.
    """
    cache_result = await db.execute(
        select(InsightCache).where(
            InsightCache.user_id == user_id,
            InsightCache.month == month,
            InsightCache.year == year,
        )
    )
    cache_row = cache_result.scalar_one_or_none()

    if cache_row is not None:
        # generated_at is stored as naive UTC; compare against now UTC
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        age = now_utc - cache_row.generated_at
        if age < timedelta(hours=CACHE_TTL_HOURS):
            try:
                data = json.loads(cache_row.insights_json)
                return InsightResponse(
                    insights=data.get("insights", []),
                    anomalies=data.get("anomalies", []),
                    suggestions=data.get("suggestions", []),
                    confidence=float(data.get("confidence", 0.0)),
                    generated_at=cache_row.generated_at,
                    cached=True,
                )
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Corrupt cache row (id=%s): %s — regenerating", cache_row.id, exc)

    return await _generate_insights(db, user_id, month, year)


async def regenerate_insights(
    db: AsyncSession,
    user_id: int,
    month: int,
    year: int,
) -> InsightResponse | InsightError:
    """
    Force-regenerate insights by deleting the cache row first,
    then calling _generate_insights.
    """
    await db.execute(
        delete(InsightCache).where(
            InsightCache.user_id == user_id,
            InsightCache.month == month,
            InsightCache.year == year,
        )
    )
    await db.commit()
    return await _generate_insights(db, user_id, month, year)
