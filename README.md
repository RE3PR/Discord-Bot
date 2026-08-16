Here’s the raw Markdown for your GitHub README. Copy everything below and paste it directly into your `README.md` file.

---

```markdown
# Discord-Bot

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

> **Note:** Qwen 3 8B is only a template. Ollama supports many other models with different sizes and capabilities. You can browse them on the [Ollama Library](https://ollama.com/library).

### 3. Set up your Discord Bot

Create a Discord application through the [Discord Developer Portal](https://discord.com/developers/applications).

Create a bot and copy its **Bot Token**.

⚠️ **Never share your Discord bot token publicly.** Treat it like a password.

### 4. Set up your `.env`

Your `.env` file should contain your Discord token and the Ollama model:

```env
DISCORD_TOKEN=your_discord_bot_token
OLLAMA_MODEL=qwen3:8b
```

Keep this file private.

### 5. Customize the Modelfile

The `Modelfile` controls your AI's personality and behavior.

For example, you can make it:

* A general-purpose AI
* A gaming assistant
* A math assistant
* A moderation assistant
* A character with a specific personality

The bot automatically uses the `Modelfile` when updating the Ollama model.

### 6. Run the bot

Open Command Prompt or PowerShell in the bot folder:

```bash
python bot.py
```

The bot will start, connect to Discord, and use your local Ollama model.

---

## 🧠 Changing the AI Model

To use a different Ollama model, first download it:

```bash
ollama pull llama3:8b
```

Then change your `.env`:

```env
OLLAMA_MODEL=llama3:8b
```

You can find other models in the [Ollama Library](https://ollama.com/library).

---

## ⚙️ Requirements

You will need:

* Windows, Linux, or macOS
* Python 3.10+
* Ollama
* A downloaded Ollama LLM
* A Discord Bot
* An internet connection for Discord

Install the required Python packages with:

```bash
pip install discord.py openai python-dotenv
```

---

## 📁 File Structure

```text
Discord-Bot/
├── bot.py
├── .env
├── Modelfile
└── README.md
```

---

## 🔒 Security

**Never upload your `.env` file to GitHub.**

Add this to your `.gitignore`:

```gitignore
.env
__pycache__/
build/
*.spec
```

Your `.env` contains your Discord bot token, so keeping it private is extremely important.

---

## 🚀 Running the Bot as an EXE

You can turn the bot into a Windows executable using PyInstaller:

```bash
pip install pyinstaller
```

Then:

```bash
pyinstaller --onefile --console bot.py
```

Your executable will be created in:

```text
dist/bot.exe
```

Keep your `Modelfile` and `.env` alongside the executable.

```text
Discord-Bot/
├── bot.exe
├── .env
└── Modelfile
```

---

## 📝 Notes

The bot runs the AI **locally through Ollama**, meaning your computer is running the LLM rather than using a cloud AI API.

The performance of the bot depends on your computer's hardware and the model you choose.

Larger models generally require more RAM/VRAM and may run slower.

---

## ⭐ Credits

Built using:

* [Ollama](https://ollama.com/)
* [Discord.py](https://discordpy.readthedocs.io/)
* [OpenAI Python Library](https://github.com/openai/openai-python)
* [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 📜 License

This project is provided for personal and educational use. Customize it, experiment with different models, and make it your own!
```
