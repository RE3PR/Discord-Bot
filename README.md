
# 🤖 Ollama Discord Bot

A modular Discord bot that integrates a local **Ollama** LLM (e.g., Llama 3, Qwen) with Discord! You can customize the bot to whatever you like.

Inside the folder you'll find a `bot.py`, `.env`, and `Modelfile`.

Here is what they do:

- `bot.py` - Your program that launches the bot (hosted locally)
- `.env` - A file with your preferences, keys, and other private data
- `Modelfile` - Controls your AI's personality, behavior, and instructions

---

## 🔨 How to Setup

### 1. Get Ollama

Download and install Ollama from the [official website](https://ollama.com/download).

### 2. Install your LLM

Open Command Prompt or PowerShell and run:

```bash
ollama pull qwen3:8b
```
This downloads the Qwen 3 8B model to your computer.
Note: Qwen 3 8B is only a template. Ollama supports many other models with different sizes and capabilities. You can browse them on the Ollama Library.
