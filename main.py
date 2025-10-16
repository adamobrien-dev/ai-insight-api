from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from typing import Literal, Optional, List, Dict
import time
from models import ImageInsightResponse, ImageAnalysisRequest

# Load environment variables and initialize OpenAI client
load_dotenv()
client = OpenAI()

# Initialize FastAPI app
app = FastAPI(title="AI Insight API")

# CORS setup — allow frontend to call API
origins = [
    "http://localhost:3000",  # Local React/Next.js frontend
    "https://adamobrien.dev",  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # ["*"] for all (not recommended for prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class PromptRequest(BaseModel):
    prompt: str
    model: Literal["gpt-4o-mini", "gpt-4-turbo"] = "gpt-4o-mini"
    temperature: float = Field(0.3, ge=0, le=1)

# --- Routes ---
@app.get("/")
def root():
    return {"service": "AI Insight API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/models")
def list_models():
    return {"available_models": ["gpt-4o-mini", "gpt-4-turbo"]}

@app.post("/analyze")
def analyze(req: PromptRequest):
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=req.model,
            messages=[{"role": "user", "content": req.prompt}],
            temperature=req.temperature
        )
        latency = round(time.time() - start, 2)
        return {
            "response": response.choices[0].message.content,
            "latency": f"{latency}s",
            "model": req.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-image", response_model=ImageInsightResponse)
async def analyze_image(req: ImageAnalysisRequest):
    start = time.time()
    try:
        result = client.chat.completions.create(
            model=req.model,
            messages=[
                {"role": "system", "content": "You are an image analysis assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": req.prompt},
                        {"type": "image_url", "image_url": {"url": req.image_url}}
                    ]
                }
            ]
        )

        # Extract the model's text response
        message = result.choices[0].message.content
        elapsed = round(time.time() - start, 2)

        # Return it in your standardized response format
        return ImageInsightResponse(
            summary=message,
            entities=[],
            text_in_image=None,
            model_used=req.model,
            tokens_used=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
