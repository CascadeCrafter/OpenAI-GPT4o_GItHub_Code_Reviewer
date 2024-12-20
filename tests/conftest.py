import pytest
from fastapi.testclient import TestClient

from app.api import app


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
def mock_github_response():
    return [{"path": "main.py", "content": "print('Hello World')", "size": 100}]


@pytest.fixture
def mock_gpt_response():
    return {
        "found_files": ["main.py"],
        "comments": ["Good code structure", "Could use more comments"],
        "rating": "8/10",
        "conclusion": "Overall good implementation",
    }
