import json
from unittest.mock import MagicMock, patch

import pytest
from openai import OpenAIError

from app.exceptions import ReviewServiceError
from app.gpt import analyze_code


@pytest.mark.asyncio
async def test_analyze_code_success():
    # Mock repository contents
    mock_contents = [
        {
            "path": "test.py",
            "content": "print('test')",
            "size": 100,
        }
    ]

    # Mock OpenAI API response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content=json.dumps(
                    {
                        "found_files": ["test.py"],
                        "comments": ["Good code structure"],
                        "rating": "8/10",
                        "conclusion": "Well implemented",
                    }
                )
            )
        )
    ]

    # Synchronous mock for OpenAI API
    with patch("app.gpt.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = await analyze_code(
            contents=mock_contents,
            description="Test assignment",
            level="Senior",
            api_key="fake-key",
        )

        # Assertions
        assert result["found_files"] == ["test.py"]
        assert "comments" in result
        assert "rating" in result
        assert "conclusion" in result
        assert result["comments"] == ["Good code structure"]
        assert result["rating"] == "8/10"
        assert result["conclusion"] == "Well implemented"


@pytest.mark.asyncio
async def test_analyze_code_api_error():
    mock_contents = [{"path": "test.py", "content": "print('test')", "size": 100}]

    with patch("openai.OpenAI") as mock_openai_class:
        # Configure the mock to raise an OpenAI error
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = OpenAIError("API Error")
        mock_openai_class.return_value = mock_client

        with pytest.raises(ReviewServiceError) as exc_info:
            await analyze_code(
                contents=mock_contents,
                description="Test assignment",
                level="Senior",
                api_key="fake-key",
            )
        assert "Unable to connect to OpenAI API" in str(exc_info.value)


@pytest.mark.asyncio
async def test_analyze_code_invalid_json():
    # Mock repository contents
    mock_contents = [{"path": "test.py", "content": "print('test')", "size": 100}]

    # Mock OpenAI API response with invalid JSON
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Invalid JSON response"))
    ]

    # Synchronous mock for OpenAI API
    with patch("app.gpt.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        # API call handled as synchronous
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        result = await analyze_code(
            contents=mock_contents,
            description="Test assignment",
            level="Senior",
            api_key="fake-key",
        )

        # Assertions
        assert result["rating"] == "N/A"
        assert "Error: AI response was not in the expected format" in result["comments"]
        assert result["conclusion"] == "Invalid JSON response"
