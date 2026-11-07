import os
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MIGRATION_PROMPT = (
    "You are an expert AWS Cloud and Python Migration Engineer.\n"
    "You refactor legacy AWS Lambda functions (Python 3.7, 3.8, 3.9) to modern Python (Python 3.12 or 3.13) running on Amazon Linux 2023.\n\n"
    "Strict Migration Rules:\n"
    "1. 'distutils' is completely removed in Python 3.12+. Replace it with standard library logic (e.g., custom string checks for boolean conversion) or 'setuptools'.\n"
    "2. 'datetime.datetime.utcnow()' is deprecated. Replace with 'datetime.datetime.now(datetime.timezone.utc)'.\n"
    "3. PEP 594 dead battery removals in 3.13: replace deprecated standard libraries like 'cgi', 'asyncore', 'asynchat', 'pipes'.\n"
    "4. Modernize type hints to Python 3.10+ built-ins (e.g., dict[str, Any], int | None).\n"
    "5. Requirements update: Update outdated pinned versions in requirements.txt to current, secure versions compatible with the target runtime.\n\n"
    "Your output must strictly conform to this JSON schema:\n"
    "{\n"
    '  "refactored_code": "string containing the full updated python code",\n'
    '  "updated_requirements": "string containing the updated requirements.txt content",\n'
    '  "summary_of_changes": ["list of strings detailing exact modifications"]\n'
    "}\n"
)

def migrate_lambda_code(source_code: str, requirements: str, target_version: str = "python3.12") -> dict:
    prompt = (
        f"Target AWS Lambda Runtime: {target_version}\n\n"
        f"SOURCE CODE:\n{source_code}\n\n"
        f"DEPENDENCIES:\n{requirements}\n"
    )

    models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash"]

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                print(f"[+] Requesting refactoring from {model_name} (Attempt {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=MIGRATION_PROMPT,
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                return json.loads(response.text)
            except ServerError:
                print("[-] Server busy (503). Retrying in 4 seconds...")
                time.sleep(4)
            except ClientError as e:
                if "404" in str(e):
                    break
                raise e
            except Exception as e:
                print(f"[-] Transient error: {e}. Retrying in 3 seconds...")
                time.sleep(3)

    raise RuntimeError("Failed to reach Gemini after retrying.")