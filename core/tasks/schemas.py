from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TaskBaseScehma(BaseModel):
    title: str = Field(
        ..., max_length=150, min_length=5, description="Tile of the task"
    )
    description: Optional[str] = Field(
        None, max_length=500, description="description of the task"
    )
    is_completed: bool = Field(..., description="State of the task")


class TaskCreateSchema(TaskBaseScehma):
    pass


class TaskUpdateScehma(TaskBaseScehma):
    pass


class TaskResponseSchema(TaskBaseScehma):
    id: int = Field(..., description="Unique identifier of the object")

    created_date: datetime = Field(
        ..., description="Creation date and time of the object"
    )
    updated_date: datetime = Field(
        ..., description="Updating date and time of the object"
    )
