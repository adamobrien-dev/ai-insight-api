from fastapi import FastAPI, HTTPException, File, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from typing import Literal, Optional, List, Dict
import time
import base64
from models import ImageInsightResponse, ImageUrlPayload

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
async def analyze_image(req: ImageUrlPayload):
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
                        {"type": "image_url", "image_url": {"url": str(req.image_url)}}
                    ]
                }
            ],
            temperature=req.temperature
        )

        # Extract the model's text response
        message = result.choices[0].message.content
        elapsed = round(time.time() - start, 2)
        
        # Get token usage from the response
        tokens_used = result.usage.total_tokens if result.usage else None

        # Return it in your standardized response format
        return ImageInsightResponse(
            summary=message,
            entities=[],
            text_in_image=None,
            model_used=req.model,
            tokens_used=tokens_used
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-file", response_model=ImageInsightResponse, status_code=status.HTTP_200_OK)
async def analyze_file(
    file: UploadFile = File(..., description="jpg/png/webp image"),
    prompt: str = "Describe this image",
    model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o-mini",
    temperature: float = 0.2,
):
    start = time.time()

    # 1) Basic validation (size/type)
    content = await file.read()

    MAX_BYTES = 5 * 1024 * 1024  # 5MB limit (tweak as needed)
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image too large (max 5MB).")

    # Detect image type from byte signatures (magic bytes)
    def detect_image_type(data: bytes) -> Optional[str]:
        if data.startswith(b'\xff\xd8\xff'):
            return "jpeg"
        elif data.startswith(b'\x89PNG\r\n\x1a\n'):
            return "png"
        elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
            return "webp"
        return None
    
    detected = detect_image_type(content)
    ct = (file.content_type or "").lower()

    # Acceptable types
    ok_types = {"image/jpeg": "jpeg", "image/png": "png", "image/webp": "webp"}
    
    # Use detected type or fall back to content-type header
    if detected:
        ext = detected
    else:
        ext = ok_types.get(ct)

    if ext not in ("jpeg", "png", "webp"):
        raise HTTPException(status_code=415, detail="Unsupported image type. Use jpg, png, or webp.")

    # 2) Convert to base64 data URL that OpenAI can read
    b64 = base64.b64encode(content).decode("utf-8")
    data_url = f"data:image/{ext};base64,{b64}"

    try:
        # 3) Call the vision model
        result = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an image analysis assistant."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            temperature=temperature,
        )

        message = result.choices[0].message.content
        tokens_used = result.usage.total_tokens if result.usage else None

        return ImageInsightResponse(
            summary=message,
            entities=[],
            text_in_image=None,
            model_used=model,
            tokens_used=tokens_used,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        elapsed = round(time.time() - start, 2)
        # (optional) print or log elapsed
