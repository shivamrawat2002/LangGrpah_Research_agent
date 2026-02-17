# Deployment Guide

## Local Development

### Prerequisites
- Python 3.10 or higher
- pip or poetry
- API keys for Firecrawl and OpenAI/Fireworks

### Setup Steps

1. **Clone or download the repository**
```bash
cd deep_research_langgraph
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. **Run the agent**
```bash
python run.py
```

## Docker Deployment

### Build Docker Image

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
```

### Build and Run
```bash
docker build -t deep-research-agent .
docker run -it --env-file .env deep-research-agent
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  research-agent:
    build: .
    env_file: .env
    volumes:
      - ./reports:/app/reports
    stdin_open: true
    tty: true
```

Run with:
```bash
docker-compose up
```


## API Server Deployment

Create a REST API wrapper:

```python
# api_server.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from deep_research import DeepResearchAgent
import uvicorn

app = FastAPI()

class ResearchRequest(BaseModel):
    query: str
    breadth: int = 4
    depth: int = 2
    follow_up_answers: list[str] = []

@app.post("/research")
async def research(request: ResearchRequest):
    agent = DeepResearchAgent(
        breadth=request.breadth,
        depth=request.depth,
    )
    
    result = await agent.run_async(
        query=request.query,
        follow_up_answers=request.follow_up_answers,
        skip_follow_up=True,
    )
    
    return {
        "report": result["final_report"],
        "learnings_count": len(result["learnings"]),
        "sources_count": len(result["sources"]),
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Install additional dependencies:
```bash
pip install fastapi uvicorn
```

Run the API:
```bash
python api_server.py
```


## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FIRECRAWL_API_KEY` | Yes | - | Firecrawl API key |
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key |
| `GOOGLE_API_KEY` | Yes* | - | GOOGLE API KEY|
| `GROQ_API_KEY` | Yes* | - | GROQ API key |
| `FIREWORKS_API_KEY` | Yes* | - | Fireworks API key (alternative) |
| `FIRECRAWL_BASE_URL` | No | API URL | Self-hosted Firecrawl URL |
| `OPENAI_ENDPOINT` | No | OpenAI | Custom OpenAI-compatible endpoint |
| `CUSTOM_MODEL` | No | Auto | Custom model name |
| `CONCURRENCY_LIMIT` | No | 3 | Max concurrent searches |

*One of LLM_API_KEY is required

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use Redis for shared state if needed
- Implement job queues (Celery, RabbitMQ) for background processing

### Vertical Scaling
- Increase memory for longer reports
- Adjust concurrency limits based on CPU cores
- Monitor API rate limits and adjust accordingly

### Cost Optimization
- Cache frequently requested research
- Implement tiered pricing based on depth/breadth
- Use cheaper LLM models for less critical tasks
- Set up spending alerts on API providers
