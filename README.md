# 🧠 AI Insight API

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-Model-grey?style=flat&logo=openai)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success)

FastAPI-powered AI analysis API that transforms natural language prompts into structured insights using OpenAI models.

---

## 🚀 Features
- `/analyze` endpoint for text → insight transformation  
- `/analyze-image` endpoint for image analysis via URL
- `/analyze-file` endpoint for direct image upload (jpg/png/webp)
- Real-time responses with request validation via Pydantic  
- Auto-generated OpenAPI docs (`/docs` and `/redoc`)  
- Lightweight and deployable via Docker  
- Health check route for monitoring uptime
- Multiple model support (GPT-4o-mini, GPT-4o, GPT-4-turbo)
- Configurable temperature for response creativity
- Image type detection via magic bytes (secure validation)
- Token usage tracking for all OpenAI API calls

---

## 💼 Example Use Cases
- Generate structured insights from survey responses  
- Summarize long documents or meeting transcripts  
- Classify text sentiment or extract key topics  
- Automate report writing or market analysis
- Analyze images for content, objects, and text extraction
- Process receipts, invoices, and documents via vision AI
- Extract structured data from screenshots and diagrams

---

## 🧩 Tech Stack
- **Backend:** FastAPI  
- **Language:** Python 3.11  
- **AI Model:** OpenAI GPT-4o  
- **Validation:** Pydantic  
- **Deployment:** AWS / Docker  

---

## ⚙️ Quick Start

```bash
# Clone the repository
git clone https://github.com/adamobrien-dev/ai-insight-api.git
cd ai-insight-api

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## 📚 API Endpoints

### `GET /`
Root endpoint with basic service information.

**Response:**
```json
{
  "service": "AI Insight API",
  "docs": "/docs"
}
```

### `GET /health`
Health check endpoint for monitoring.

**Response:**
```json
{
  "ok": true
}
```

### `GET /models`
List available AI models.

**Response:**
```json
{
  "available_models": ["gpt-4o-mini", "gpt-4-turbo"]
}
```

### `POST /analyze`
Main analysis endpoint that processes prompts using OpenAI.

**Request Body:**
```json
{
  "prompt": "Explain quantum computing in simple terms",
  "model": "gpt-4o-mini",
  "temperature": 0.3
}
```

**Parameters:**
- `prompt` (string, required): Your input text/question
- `model` (string, optional): Model to use - `"gpt-4o-mini"` or `"gpt-4-turbo"` (default: `"gpt-4o-mini"`)
- `temperature` (float, optional): Creativity level 0-1 (default: `0.3`)

**Response:**
```json
{
  "response": "Quantum computing is a type of computing that...",
  "latency": "1.23s",
  "model": "gpt-4o-mini"
}
```

---

### `POST /analyze-image`
Analyze images from public URLs using OpenAI's vision models.

**Request Body:**
```json
{
  "image_url": "https://example.com/image.jpg",
  "prompt": "Describe this image and extract entities",
  "model": "gpt-4o",
  "temperature": 0.2
}
```

**Parameters:**
- `image_url` (string, required): Publicly accessible HTTPS URL to the image
- `prompt` (string, optional): Analysis instruction (default: `"Describe the image and extract entities."`)
- `model` (string, optional): Vision model - `"gpt-4o"` or `"gpt-4o-mini"` (default: `"gpt-4o"`)
- `temperature` (float, optional): Creativity level 0-1 (default: `0.2`)

**Response:**
```json
{
  "summary": "The image shows a modern office with...",
  "entities": [],
  "text_in_image": null,
  "model_used": "gpt-4o",
  "tokens_used": 1247
}
```

---

### `POST /analyze-file`
Upload and analyze images directly (multipart form data).

**Features:**
- Support multipart image uploads (jpg/png/webp)
- 5MB file size cap for security
- Magic byte detection for secure image type validation
- Convert to base64 data URL and call GPT-4o-mini vision
- Return standardized ImageInsightResponse with token usage

**Request (multipart/form-data):**
```bash
# Using cURL
curl -X POST "http://localhost:8000/analyze-file" \
  -F "file=@/path/to/image.jpg" \
  -F "prompt=Describe this image" \
  -F "model=gpt-4o-mini" \
  -F "temperature=0.2"
```

**Parameters:**
- `file` (file, required): Image file (jpg/png/webp, max 5MB)
- `prompt` (string, optional): Analysis instruction (default: `"Describe this image"`)
- `model` (string, optional): Vision model - `"gpt-4o"` or `"gpt-4o-mini"` (default: `"gpt-4o-mini"`)
- `temperature` (float, optional): Creativity level 0-1 (default: `0.2`)

**Response:**
```json
{
  "summary": "The image contains a receipt from...",
  "entities": [],
  "text_in_image": null,
  "model_used": "gpt-4o-mini",
  "tokens_used": 892
}
```

**Error Responses:**
- `413`: Image too large (exceeds 5MB limit)
- `415`: Unsupported image type (only jpg/png/webp allowed)
- `500`: Processing error

---

## 🧾 Response Schema
All responses follow this structure:
```json
{
  "response": "<model_output>",
  "latency": "<processing_time>",
  "model": "<model_name>"
}
```

---

## 🧪 Usage Examples

### Text Analysis

#### Using cURL
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What are the benefits of FastAPI?",
    "model": "gpt-4o-mini",
    "temperature": 0.3
  }'
```

#### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "prompt": "What are the benefits of FastAPI?",
        "model": "gpt-4o-mini",
        "temperature": 0.3
    }
)
print(response.json())
```

#### Using JavaScript/Node.js
```javascript
fetch('http://localhost:8000/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'What are the benefits of FastAPI?',
    model: 'gpt-4o-mini',
    temperature: 0.3
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

### Image Analysis (URL)

#### Using cURL
```bash
curl -X POST "http://localhost:8000/analyze-image" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/receipt.jpg",
    "prompt": "Extract the total amount and merchant name",
    "model": "gpt-4o",
    "temperature": 0.2
  }'
```

#### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/analyze-image",
    json={
        "image_url": "https://example.com/photo.jpg",
        "prompt": "What objects are in this image?",
        "model": "gpt-4o-mini",
        "temperature": 0.2
    }
)
print(response.json())
```

---

### Image Analysis (File Upload)

#### Using cURL
```bash
curl -X POST "http://localhost:8000/analyze-file" \
  -F "file=@./invoice.png" \
  -F "prompt=Extract invoice details" \
  -F "model=gpt-4o-mini" \
  -F "temperature=0.2"
```

#### Using Python
```python
import requests

with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze-file",
        files={"file": f},
        data={
            "prompt": "Describe this image in detail",
            "model": "gpt-4o-mini",
            "temperature": 0.2
        }
    )
print(response.json())
```

#### Using JavaScript (Browser)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('prompt', 'Describe this image');
formData.append('model', 'gpt-4o-mini');
formData.append('temperature', '0.2');

fetch('http://localhost:8000/analyze-file', {
  method: 'POST',
  body: formData
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

---

## 📖 Interactive Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🚢 Deployment

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ai-insight-api .
docker run -d -p 8000:8000 --env-file .env ai-insight-api
```

Access the API at `http://<your-server-ip>:8000/docs`

### AWS EC2 / Cloud Deployment
To deploy on AWS EC2 or similar cloud platforms:

1. **SSH into your server:**
   ```bash
   ssh -i your-key.pem ubuntu@your-server-ip
   ```

2. **Install Docker (if not already installed):**
   ```bash
   sudo apt update
   sudo apt install docker.io -y
   sudo systemctl start docker
   ```

3. **Clone and deploy:**
   ```bash
   git clone https://github.com/adamobrien-dev/ai-insight-api.git
   cd ai-insight-api
   echo "OPENAI_API_KEY=your_key_here" > .env
   docker build -t ai-insight-api .
   docker run -d -p 8000:8000 --env-file .env --restart unless-stopped ai-insight-api
   ```

4. **Access your API:**
   - Visit `http://<your-server-ip>:8000/docs`
   - Configure security groups to allow port 8000

---

## 🛠️ Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (if available)
pytest
```

---

## 📝 License

MIT License - feel free to use this project for your own purposes.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Contact

For questions or support:
- **Email:** hi@adamobrien.dev
- **GitHub Issues:** [Report bugs or request features](https://github.com/adamobrien-dev/ai-insight-api/issues)

---

🧠 Built with ❤️ by [Adam O'Brien](https://adamobrien.dev)

