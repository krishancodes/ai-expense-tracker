from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class InsightResponse(BaseModel):
    """Successful LLM-generated (or cached) insight response."""

    insights: List[str]
    anomalies: List[str]
    suggestions: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    generated_at: datetime
    cached: bool


class InsightError(BaseModel):
    """Returned when the LLM call fails; never raises a 500."""

    insights: List[str] = []
    anomalies: List[str] = []
    suggestions: List[str] = []
    confidence: float = 0.0
    error: str
    cached: bool = False
