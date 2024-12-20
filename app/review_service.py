from typing import Dict

from app.exceptions import ReviewServiceError
from app.github import fetch_repository_files
from app.gpt import analyze_code


async def perform_code_review(
    request: dict, github_token: str, openai_key: str
) -> Dict:
    """
    Main service for performing the code review.

    Args:
        request (dict): Contains 'github_repo_url', 'assignment_description', and 'candidate_level'
        github_token (str): GitHub authentication token
        openai_key (str): OpenAI API key

    Returns:
        Dict: Review results containing analysis and recommendations

    Raises:
        ReviewServiceError: If required fields are missing or service errors occur
    """
    try:
        # Validate required fields
        required_fields = [
            "github_repo_url",
            "assignment_description",
            "candidate_level",
        ]
        for field in required_fields:
            if not request.get(field):
                raise ReviewServiceError(f"Missing required field: {field}")

        # Fetch the contents of the GitHub repository
        repo_contents = await fetch_repository_files(
            request["github_repo_url"], github_token
        )
        if not repo_contents:
            raise ReviewServiceError("No files found in repository")

        # Call OpenAI GPT for an analysis based on the repository and description
        review_result = await analyze_code(
            contents=repo_contents,
            description=request["assignment_description"],
            level=request["candidate_level"],
            api_key=openai_key,
        )

        return {"status": "success", **review_result}

    except ReviewServiceError as e:
        raise e
    except Exception as e:
        raise ReviewServiceError(f"Error performing code review: {str(e)}")
