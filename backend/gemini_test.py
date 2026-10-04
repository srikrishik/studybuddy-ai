import os
from google import genai

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

response = client.models.generate_content(
    model="gemma-4-26b-a4b-it",
    contents="Explain photosynthesis in 3 simple sentences for a student."
)

print("\nGemma response:\n")
print(response.text)

client.close()