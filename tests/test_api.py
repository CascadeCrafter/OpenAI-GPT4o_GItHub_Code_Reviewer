from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import ReviewServiceError


def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_missing_env_vars(test_client, monkeypatch):
    # Clear environment variables
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = test_client.post(
        "/review",
        json={
            "github_repo_url": "https://github.com/user/repo",
            "assignment_description": "Test assignment",
            "candidate_level": "Senior",
        },
    )
    assert response.status_code == 500
    assert "Missing required environment variables" in response.json()["detail"]


@pytest.mark.asyncio
async def test_successful_review(test_client, mock_github_response, mock_gpt_response):
    with patch(
        "app.review_service.fetch_repository_files", new_callable=AsyncMock
    ) as mock_fetch, patch(
        "app.review_service.analyze_code", new_callable=AsyncMock
    ) as mock_analyze:

        mock_fetch.return_value = mock_github_response
        mock_analyze.return_value = mock_gpt_response

        response = test_client.post(
            "/review",
            json={
                "github_repo_url": "https://github.com/user/repo",
                "assignment_description": "Test assignment",
                "candidate_level": "Senior",
            },
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "found_files" in response.json()
        assert "comments" in response.json()


@pytest.mark.asyncio
async def test_review_service_error(test_client):
    with patch(
        "app.review_service.fetch_repository_files", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.side_effect = ReviewServiceError("Repository not found")

        response = test_client.post(
            "/review",
            json={
                "github_repo_url": "https://github.com/user/repo",
                "assignment_description": "Test assignment",
                "candidate_level": "Senior",
            },
        )

        assert response.status_code == 400
        assert "Repository not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_request_data(test_client):
    response = test_client.post(
        "/review",
        json={
            "github_repo_url": "not-a-valid-url",
            "assignment_description": "Test assignment",
            "candidate_level": "Senior",
        },
    )
    assert response.status_code == 422
