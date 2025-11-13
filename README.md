# Zoom AI Agent

A Slack bot that leverages LangChain and OpenAI to answer questions about your company using a RAG (Retrieval-Augmented Generation) system.

## Features

- Slack integration via Socket Mode
- Vector database search using Chroma
- Company knowledge base queries
- OpenAI GPT-4o-mini powered responses

## Prerequisites

- Python 3.13+
- OpenAI API key
- Slack app with Bot Token and App Token
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
   - `SLACK_BOT_TOKEN` - Your Slack bot OAuth token (xoxb-)
   - `SLACK_APP_TOKEN` - Your Slack app token (xoxa-)

4. **Add knowledge base**
   Place `.txt` files in the `docs/` directory for the bot to learn from.

5. **Run the bot**
   ```bash
   uv run python main.py
   ```

## Usage

Mention the bot in Slack channels or DMs to ask questions about your company. The bot will search the knowledge base and provide relevant answers.

## Project Structure

- `main.py` - Main Slack bot application
- `tools/search.py` - Vector store initialization and search functionality  
- `docs/` - Knowledge base text files
- `chroma_langchain_db/` - Vector database storage


--

```
ngrok start teamchat chatbot
```