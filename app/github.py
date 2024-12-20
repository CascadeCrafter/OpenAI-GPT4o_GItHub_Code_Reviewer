from typing import Dict, List
from urllib.parse import urlparse

import httpx

from app.exceptions import ReviewServiceError

GITHUB_API_BASE = "https://api.github.com"
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".cs",
    ".go",
    ".rb",
    ".php",
}


async def fetch_repository_files(repo_url: str, token: str) -> List[Dict]:
    """
    Fetches all files in the specified GitHub repository.

    Args:
        repo_url (str): Full GitHub repository URL
        token (str): GitHub authentication token

    Returns:
        List[Dict]: List of file objects containing path and content

    Raises:
        ReviewServiceError: If there are issues accessing the repository
    """
    GITHUB_API_BASE = "https://api.github.com"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        # Parse and validate the GitHub URL
        parsed_url = urlparse(repo_url)
        if parsed_url.netloc != "github.com":
            raise ReviewServiceError(
                "Invalid GitHub URL. Must be a github.com repository"
            )

        # Extract the user and repo name from the URL
        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2:
            raise ReviewServiceError("Invalid repository path")
        user, repo = path_parts[:2]

        # Fetch repository contents
        api_url = f"{GITHUB_API_BASE}/repos/{user}/{repo}/contents"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers, timeout=30.0)

            if response.status_code == 404:
                raise ReviewServiceError("Repository not found")
            elif response.status_code == 403:
                raise ReviewServiceError(
                    "Access denied. Check GitHub token permissions"
                )
            elif response.status_code != 200:
                error_data = response.json()
                raise ReviewServiceError(
                    f"GitHub API Error: {error_data.get('message', 'Unknown error')}"
                )

            contents = response.json()
            return await _process_repository_contents(contents, client, headers)
    except Exception as e:
        raise ReviewServiceError(f"An unexpected error occurred: {str(e)}")


async def _process_repository_contents(
    contents: List[Dict], client: httpx.AsyncClient, headers: Dict
) -> List[Dict]:
    """
    Recursively processes repository contents, fetching file contents when needed.

    Args:
        contents (List[Dict]): List of file/directory objects from GitHub API
        client (httpx.AsyncClient): HTTP client for making requests
        headers (Dict): GitHub API headers

    Returns:
        List[Dict]: Processed list of file objects with contents
    """
    processed_files = []

    for item in contents:
        if item["type"] == "file":
            # Only process supported file types
            if any(item["name"].endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                response = await client.get(item["download_url"], headers=headers)
                if response.status_code == 200:
                    processed_files.append(
                        {
                            "path": item["path"],
                            "content": response.text,
                            "size": item["size"],
                        }
                    )
        elif item["type"] == "dir":
            # Recursively fetch directory contents
            response = await client.get(item["url"], headers=headers)
            if response.status_code == 200:
                sub_contents = response.json()
                processed_files.extend(
                    await _process_repository_contents(sub_contents, client, headers)
                )

    return processed_files
