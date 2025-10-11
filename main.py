from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = FastAPI()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/analyze")
def analyze(request: PromptRequest):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": request.prompt}]
    )
    return {"response": response.choices[0].message.content}
