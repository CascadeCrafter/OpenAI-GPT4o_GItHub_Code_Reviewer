from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.exceptions import ReviewServiceError
from app.github import fetch_repository_files


@pytest.mark.asyncio
async def test_fetch_repository_files_success():
    mock_contents = [
        {
            "type": "file",
            "name": "test.py",
            "path": "test.py",
            "download_url": "https://raw.githubusercontent.com/user/repo/main/test.py",
            "size": 100,
        }
    ]

    with patch("httpx.AsyncClient") as mock_client:
        # Mock first response (repository contents)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_contents

        # Mock second response (file content)
        mock_file_response = Mock()
        mock_file_response.status_code = 200
        mock_file_response.text = "print('test')"

        # Set up mocked AsyncClient
        mock_client_instance = AsyncMock()
        mock_client_instance.get.side_effect = [mock_response, mock_file_response]
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        # Call the actual function
        result = await fetch_repository_files(
            "https://github.com/user/repo", "fake-token"
        )

        # Assertions
        assert len(result) == 1
        assert result[0]["path"] == "test.py"
        assert result[0]["content"] == "print('test')"

        # Verify calls for correctness
        mock_client_instance.get.assert_any_call(
            "https://api.github.com/repos/user/repo/contents",
            headers={
                "Authorization": "Bearer fake-token",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30.0,
        )


@pytest.mark.asyncio
async def test_fetch_repository_files_invalid_url():
    with pytest.raises(ReviewServiceError) as exc_info:
        await fetch_repository_files("https://invalid-url.com/user/repo", "fake-token")
    assert "Invalid GitHub URL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_repository_files_not_found():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.json = AsyncMock(return_value={"message": "Not Found"})

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(ReviewServiceError) as exc_info:
            await fetch_repository_files("https://github.com/user/repo", "fake-token")
        assert "Repository not found" in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_repository_files_access_denied():
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 403
        mock_response.json = AsyncMock(return_value={"message": "Access Denied"})

        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        with pytest.raises(ReviewServiceError) as exc_info:
            await fetch_repository_files("https://github.com/user/repo", "fake-token")
        assert "Access denied" in str(exc_info.value)
