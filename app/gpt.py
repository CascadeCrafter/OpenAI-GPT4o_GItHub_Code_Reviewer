import json
from typing import Dict, List

from openai import OpenAI, OpenAIError

from app.exceptions import ReviewServiceError


async def analyze_code(
    contents: List[dict], description: str, level: str, api_key: str
) -> Dict:
    """
    Use OpenAI GPT to analyze the provided repository contents.

    Args:
        contents (List[dict]): List of files with their contents.
        description (str): Assignment description.
        level (str): Expected candidate level.
        api_key (str): OpenAI API key.

    Returns:
        Dict: Analysis results, including code quality, issues, and rating.

    Raises:
        ReviewServiceError: If analysis fails or API issues occur.
    """
    try:
        # Prepare the code content for analysis
        code_contents = [
            f"File: {file['path']}\n" f"```\n{file['content'][:1000]}...\n```\n"
            for file in contents
        ]

        # Create a structured prompt
        prompt = (
            f"You are performing a code review for a candidate's assignment.\n\n"
            f"Assignment Details:\n"
            f"- Description: {description}\n"
            f"- Expected Level: {level}\n\n"
            f"Repository Contents:\n"
            f"{chr(10).join(code_contents)}\n\n"
            f"Please provide a detailed technical analysis including:\n"
            f"1. Code Quality Assessment:\n"
            f"   - Code organization and structure\n"
            f"   - Naming conventions and readability\n"
            f"   - Error handling and edge cases\n"
            f"   - Documentation and comments\n\n"
            f"2. Technical Issues:\n"
            f"   - Potential bugs or vulnerabilities\n"
            f"   - Performance concerns\n"
            f"   - Architecture problems\n"
            f"   - Missing tests or validation\n\n"
            f"3. Improvement Suggestions:\n"
            f"   - Specific recommendations for better code quality\n"
            f"   - Best practices that should be applied\n"
            f"   - Additional features or enhancements\n\n"
            f"4. Overall Rating:\n"
            f"   - Score out of 10\n"
            f"   - Brief justification for the score\n\n"
            f"Please provide a code review analysis in the following JSON format:\n"
            "{\n"
            '  "found_files": ["list of all analyzed files"],\n'
            '  "comments": ["detailed list of comments and suggestions about code quality, '
            'technical issues, and improvement suggestions"],\n'
            '  "rating": "score out of 10 with brief justification",\n'
            '  "conclusion": "detailed technical conclusion summarizing the review"\n'
            "}\n\n"
            "Ensure the response is properly formatted JSON."
        )

        client = OpenAI(api_key=api_key)
        MODEL = "gpt-4o"
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced technical lead performing a detailed code review.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        raw_analysis = completion.choices[0].message.content

        # Clean up the response by removing code block markers if present
        cleaned_response = raw_analysis.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]

        try:
            # Parse the response as JSON
            parsed_analysis = json.loads(cleaned_response)
            # Return the structured response
            return {
                "found_files": [file["path"] for file in contents],
                "comments": parsed_analysis.get("comments", []),
                "rating": parsed_analysis.get("rating", "N/A"),
                "conclusion": parsed_analysis.get(
                    "conclusion", "Analysis failed to provide a conclusion"
                ),
            }
        except json.JSONDecodeError as json_err:
            # Handle case where response isn't valid JSON
            return {
                "found_files": [file["path"] for file in contents],
                "comments": ["Error: AI response was not in the expected format"],
                "rating": "N/A",
                "conclusion": raw_analysis,
            }

    except OpenAIError as req_err:
        # Handle general communication errors, such as connection or DNS issues
        raise ReviewServiceError(
            f"Unable to connect to OpenAI API: {str(req_err)}"
        ) from req_err
    except KeyError as key_err:
        # Handle unexpected structure in the API response
        raise ReviewServiceError(
            f"Unexpected API response format: {str(key_err)}"
        ) from key_err
    except Exception as e:
        # Handle any other unforeseen exceptions
        raise ReviewServiceError(f"Error during code analysis: {str(e)}") from e
