# AI Engine Architecture Overview

## Module Positioning

`ai-engine` is an independent Python AI service for:

- multi-turn chat
- RAG retrieval
- homework grading
- OCR integration
- difficulty ranking

Core files:

- `api/main.py`
- `services/service_manager.py`

## Main Structure

- `api/`: FastAPI routes
- `services/`: core AI services
- `config/`: runtime configuration
- `models/`: model assets
- `data/`: RAG knowledge source
- `tests/`: tests and validation scripts

Registered services:

- `embedding`
- `llm`
- `chat`
- `grading`
- `difficulty`
- `ocr`
- `rag`
- `session_history`

## Core Capabilities

### Chat

- uses `LLMService`
- supports session-based multi-turn conversation
- supports optional RAG-enhanced answering

### RAG

- uses `know.md` as the current knowledge source
- uses Bailian embeddings + Chroma for retrieval
- supports persistence, cache, and rebuild

### Grading

- supports text grading
- supports code grading
- supports image grading through OCR -> text -> grading

### Difficulty Ranking

- uses handcrafted features
- uses Bailian embedding vectors
- uses XGBoost for prediction

### OCR

- uses Bailian OCR models
- returns normalized `text/items/confidence` structure to callers

## Deployment

Relevant files:

- `docker-compose.yml`
- `Dockerfile`

Main service:

- `ai-engine`
