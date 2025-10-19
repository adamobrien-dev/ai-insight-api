# models.py
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, AnyHttpUrl, field_validator, model_validator

# ===== Request Models =====

class ImageUrlPayload(BaseModel):
    """
    Use when the client sends a public image URL (jpeg/png/webp).
    """
    image_url: AnyHttpUrl = Field(
        ...,
        description="Publicly accessible URL to the image (https)."
    )
    prompt: str = Field(
        "Describe the image and extract entities.",
        min_length=1,
        description="Instruction for what to extract or describe."
    )
    model: Literal["gpt-4o", "gpt-4o-mini"] = Field(
        "gpt-4o",
        description="Vision-capable model."
    )
    temperature: float = Field(
        0.2, ge=0.0, le=1.0,
        description="Creativity vs determinism (0–1)."
    )

    @field_validator("prompt")
    @classmethod
    def _trim_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Prompt cannot be empty after trimming.")
        return v


class ImageFilePayload(BaseModel):
    """
    Use alongside UploadFile fields in a multipart form. The binary file itself
    is NOT in this model; it’s handled by FastAPI's UploadFile param.
    """
    prompt: str = Field(
        "Describe the image and extract entities.",
        min_length=1
    )
    model: Literal["gpt-4o", "gpt-4o-mini"] = "gpt-4o"
    temperature: float = Field(0.2, ge=0.0, le=1.0)

    @field_validator("prompt")
    @classmethod
    def _trim_prompt(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Prompt cannot be empty after trimming.")
        return v


# ===== Response Models =====

class DetectedEntity(BaseModel):
    """
    Lightweight tag or extracted item (e.g., 'person', 'total_amount').
    """
    label: str = Field(..., min_length=1, description="Entity name.")
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Optional confidence in [0,1]."
    )


class ImageInsightResponse(BaseModel):
    """
    Standard response for image analysis endpoints.
    """
    summary: str = Field(..., min_length=1, description="Concise description/insight.")
    entities: List[DetectedEntity] = Field(
        default_factory=list,
        description="Extracted entities/tags."
    )
    text_in_image: Optional[str] = Field(
        default=None,
        description="OCR-like text if present, else null."
    )
    model_used: str = Field(..., description="Actual model used.")
    tokens_used: Optional[int] = Field(
        default=None, ge=0,
        description="Token usage if available."
    )

    @model_validator(mode="after")
    def _ensure_non_empty_content(self):
        """
        Guard against returning an empty response object if upstream fails.
        Require either a non-empty summary or non-empty text_in_image.
        """
        has_summary = bool(self.summary and self.summary.strip())
        has_text = bool(self.text_in_image and self.text_in_image.strip()) if self.text_in_image else False
        if not (has_summary or has_text):
            raise ValueError("Response must contain a non-empty summary or text_in_image.")
        return self


class ImageAnalysisRequest(BaseModel):
    image_url: str
    prompt: Optional[str] = "Describe this image"
    model: Optional[str] = "gpt-4o-mini"


# ===== Batch Processing Models =====

class AnalyzeItem(BaseModel):
    """
    Single item for batch analysis - can be text or image.
    """
    prompt: str = Field(..., min_length=1, description="Prompt to analyze")
    image_url: Optional[AnyHttpUrl] = Field(
        None,
        description="Optional image URL. If provided, performs image analysis."
    )
    model: Optional[Literal["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)


class AnalyzeBatchRequest(BaseModel):
    """
    Request model for batch analysis endpoint.
    """
    items: List[AnalyzeItem] = Field(
        ...,
        min_length=1,
        max_length=10,  # Limit batch size for safety
        description="List of items to analyze (max 10)"
    )


class AnalyzeBatchResponse(BaseModel):
    """
    Response model for batch analysis endpoint.
    """
    results: List[dict] = Field(
        ...,
        description="List of results corresponding to input items"
    )