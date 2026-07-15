import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def ask_gemini(question: str) -> str:
    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=question
    )
    return interaction.output_text

print("AI 챗봇 시작 (종료: exit)")
while True:
    question = input("\nUser: ")

    if question.lower() == "exit":
        break

    answer = ask_gemini(question)

    print("\nAI:", answer)