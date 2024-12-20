import json

import requests


def test_code_review_api():
    url = "http://localhost:8000/review"

    payload = {
        "github_repo_url": "https://github.com/bast/somepackage",
        "assignment_description": "Show how to structure a Python project.",
        "candidate_level": "Senior",
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    test_code_review_api()
