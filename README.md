# Zoom Team Chat AI Agent

A Zoom Team Chat bot that leverages LangChain and OpenAI to answer questions about your company using a RAG (Retrieval-Augmented Generation) system.

## Features

- Zoom Team Chat integration via webhooks
- Vector database search using Chroma
- Company knowledge base queries
- OpenAI GPT-4o-mini powered responses

## Prerequisites

- Python 3.13+
- OpenAI API key
- Zoom Team Chat app with webhook configuration
- uv package manager

## Quick Start

1. **Clone and setup environment**
   ```bash
   git clone <repository-url>
   cd zoom-ai-agent
   cp .env.example .env
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   Edit `.env` with your keys:
   - `OPENAI_API_KEY` - Your OpenAI API key
   - `ZOOM_CLIENT_ID` - Your Zoom app Client ID
   - `ZOOM_CLIENT_SECRET` - Your Zoom app Client Secret
   - `ZOOM_WEBHOOK_SECRET_TOKEN` - Your Zoom webhook secret token

4. **Add knowledge base**
   Place `.txt` files in the `docs/` directory for the bot to learn from.

5. **Run the bot**
   ```bash
   uv run python main.py
   ```

## Usage

Mention the bot in Zoom Team Chat channels or DMs to ask questions about your company. The bot will search the knowledge base and provide relevant answers.

## Project Structure

- `main.py` - Main Zoom Team Chat bot application
- `zoom/` - Zoom Team Chat integration modules
  - `webhook.py` - Webhook handler for Zoom Team Chat events
  - `client.py` - Zoom API client for sending messages
- `tools/search.py` - Vector store initialization and search functionality  
- `docs/` - Knowledge base text files
- `chroma_langchain_db/` - Vector database storage