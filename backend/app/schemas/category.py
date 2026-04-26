from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    is_system: bool
    user_id: Optional[int]


class CreateCategoryRequest(BaseModel):
    name: str = Field(..., max_length=50)
    icon: Optional[str] = None
    color: Optional[str] = None


class UpdateCategoryRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    icon: Optional[str] = None
    color: Optional[str] = None
