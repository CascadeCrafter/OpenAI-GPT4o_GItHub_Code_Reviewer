import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from app.exceptions import ReviewServiceError
from app.review_service import perform_code_review

app = FastAPI(title="Code Review API")


class CodeReviewRequest(BaseModel):
    github_repo_url: HttpUrl
    assignment_description: str
    candidate_level: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "github_repo_url": "https://github.com/username/repo",
                "assignment_description": "Build a REST API with user authentication",
                "candidate_level": "Senior",
            }
        }
    }


async def get_tokens():
    github_token = os.getenv("GITHUB_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not github_token or not openai_key:
        raise HTTPException(
            status_code=500, detail="Missing required environment variables"
        )
    return github_token, openai_key


@app.post("/review")
async def create_code_review(
    request: CodeReviewRequest, tokens: tuple = Depends(get_tokens)
):
    """
    Create a code review for a GitHub repository
    """
    github_token, openai_key = tokens

    request_data = request.model_dump()
    request_data["github_repo_url"] = str(request.github_repo_url)

    try:
        result = await perform_code_review(
            request=request_data, github_token=github_token, openai_key=openai_key
        )
        return result
    except ReviewServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint
    """
    return {"status": "healthy"}
