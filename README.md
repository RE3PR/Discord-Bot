# Discord-Bot

# 🤖 Ollama Discord Bot

A modular Discord bot that integrates a local **Ollama** LLM (e.g., Llama 3, Qwen) with powerful moderation commands and an auto‑updating `Modelfile` system. The bot automatically rebuilds its AI model from the `Modelfile` every time it starts, so you can quickly iterate on prompts and behavior.

---

## ✨ Features

- **AI Chat** – Responds to messages that mention the bot or contain configurable trigger words.
- **Auto‑Model Update** – On every launch, the bot runs `ollama create <model> -f Modelfile` – your latest prompt changes are applied instantly.
- **Moderation Commands** – Kick, ban, timeout, clear, lock, warn, slowmode, and more.
- **User/Server Info** – Quick commands to display member and server details.
- **Configurable Triggers** – Set custom trigger words (e.g., `bonnie`, `blue`, `bot`) via `.env` – no code changes needed.
- **Secure Token Handling** – Discord token and model name stored in `.env` – never hard‑coded.
- **Cross‑Platform** – Works on Windows, Linux, and macOS (with Ollama installed).

---

## 📦 Prerequisites

- **Python 3.8+** – [Download](https://python.org)
- **Ollama** – [Install](https://ollama.ai/) and have at least one base model pulled (e.g., `ollama pull llama3:8b`).
- **Discord Bot Token** – [Create a bot](https://discord.com/developers/applications) and invite it to your server with the required permissions.

---

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
