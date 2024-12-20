from typing import Dict, List, Literal

from pydantic import BaseModel, HttpUrl, field_validator


class ReviewRequest(BaseModel):
    assignment_description: str
    github_repo_url: HttpUrl
    candidate_level: Literal["Junior", "Middle", "Senior"]

    @field_validator("assignment_description")
    def validate_description(cls, v):
        if not v.strip():
            raise ValueError("Assignment description cannot be empty")
        return v.strip()


class ReviewResponse(BaseModel):
    found_files: List[str]
    comments: Dict[str, List[str]]
    rating: int
    conclusion: str
