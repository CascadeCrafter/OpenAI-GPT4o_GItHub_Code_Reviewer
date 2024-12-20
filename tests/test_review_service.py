from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import ReviewServiceError
from app.review_service import perform_code_review


@pytest.mark.asyncio
async def test_perform_code_review_success():
    mock_request = {
        "github_repo_url": "https://github.com/user/repo",
        "assignment_description": "Test assignment",
        "candidate_level": "Senior",
    }

    mock_github_response = [
        {"path": "test.py", "content": "print('test')", "size": 100}
    ]

    mock_gpt_response = {
        "found_files": ["test.py"],
        "comments": ["Good code"],
        "rating": "8/10",
        "conclusion": "Well done",
    }

    mock_fetch = AsyncMock(return_value=mock_github_response)
    mock_analyze = AsyncMock(return_value=mock_gpt_response)

    with patch("app.review_service.fetch_repository_files", mock_fetch), patch(
        "app.review_service.analyze_code", mock_analyze
    ):

        result = await perform_code_review(
            request=mock_request, github_token="fake-token", openai_key="fake-key"
        )

        mock_fetch.assert_called_once_with(
            mock_request["github_repo_url"], "fake-token"
        )

        assert result["status"] == "success"
        assert "found_files" in result
        assert "comments" in result
        assert "rating" in result


@pytest.mark.asyncio
async def test_perform_code_review_missing_fields():
    mock_request = {
        "github_repo_url": "https://github.com/user/repo"
        # Missing required fields
    }

    with pytest.raises(ReviewServiceError) as exc_info:
        await perform_code_review(
            request=mock_request, github_token="fake-token", openai_key="fake-key"
        )
    assert "Missing required field" in str(exc_info.value)
