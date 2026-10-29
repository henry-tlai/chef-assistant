from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(http_options=types.HttpOptions(timeout=30000))  # 30 sec, in milliseconds
print("Sending request...")

try:
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Give me a quick dinner idea using chicken and rice.",
    )
    for part in response.candidates[0].content.parts:
        if part.text:
            print("TEXT:", part.text)
        elif part.inline_data:
            print("NON-TEXT:", part.inline_data.mime_type)

except Exception as e:
    print("Error:", type(e).__name__, e)