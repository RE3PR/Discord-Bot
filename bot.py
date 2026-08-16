import os
import json
import asyncio
import discord
from discord.ext import commands
from openai import OpenAI
from dotenv import load_dotenv, set_key
import datetime
import sys
import re
import subprocess

# ---------- BETA NOTICE ----------
print("╔══════════════════════════════════════════════════╗")
print("║            B O T   I S   I N   B E T A          ║")
print("║  Use at your own risk – features may change     ║")
print("╚══════════════════════════════════════════════════╝\n")

load_dotenv()

# ---------- Helper to get token/model (prompt only if missing) ----------
def get_or_prompt(var_name, env_key, prompt_message):
    value = os.getenv(env_key)
    if not value:
        while True:
            value = input(prompt_message).strip()
            if value:
                break
            print("Value cannot be empty. Please try again.")
        set_key(".env", env_key, value)
        os.environ[env_key] = value
    return value

# Get initial values (only prompt if not in .env)
DISCORD_TOKEN = get_or_prompt("DISCORD_TOKEN", "DISCORD_TOKEN", "Enter your Discord API token: ")
MODEL = get_or_prompt("OLLAMA_MODEL", "OLLAMA_MODEL", "Enter your Ollama model name: ")

# ---------- Get trigger names (comma-separated) ----------
def get_trigger_names():
    # Check if TRIGGER_NAMES is in .env
    trigger_env = os.getenv("TRIGGER_NAMES")
    if trigger_env:
        # Split by comma and strip whitespace
        names = [name.strip() for name in trigger_env.split(",") if name.strip()]
        if names:
            return names
    # If not set or empty, prompt user
    print("\n" + "=" * 50)
    print("Set trigger words that will make the bot respond.")
    print("Example: bonnie, blue, bot, ai")
    print("Leave empty to only respond when mentioned directly.")
    trigger_input = input("Enter trigger names (comma-separated): ").strip()
    if trigger_input:
        names = [name.strip() for name in trigger_input.split(",") if name.strip()]
        if names:
            # Save to .env for next time
            set_key(".env", "TRIGGER_NAMES", trigger_input)
            os.environ["TRIGGER_NAMES"] = trigger_input
            return names
    return []  # No trigger names – only direct mentions will trigger

AI_NAME_VARIATIONS = get_trigger_names()

# ---------- Auto-update model from Modelfile (fixed) ----------
async def update_model_from_modelfile(model_name):
    """Update the Ollama model from Modelfile with real-time output."""
    # Use script directory so Modelfile is always found
    script_dir = os.path.dirname(os.path.abspath(__file__))
    modelfile_path = os.path.join(script_dir, "Modelfile")
    
    if not os.path.exists(modelfile_path):
        print("\n⚠️  No Modelfile found next to bot.py.")
        print(f"   Using existing model '{model_name}' (if it exists).")
        return False
    
    print("\n" + "=" * 60)
    print(f"📄 Modelfile: {modelfile_path}")
    print(f"🤖 Model:     {model_name}")
    print("=" * 60)
    
    def run_update():
        try:
            print("\n🛠️ Creating/updating model...")
            print(f"   ollama create {model_name} -f \"{modelfile_path}\"\n")
            
            process = subprocess.Popen(
                [
                    "ollama",
                    "create",
                    model_name,
                    "-f",
                    modelfile_path
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore",
                bufsize=1
            )
            
            # Show Ollama's output in real time
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(f"   {line}")
            
            process.wait()
            
            if process.returncode == 0:
                return True
            
            print(f"\n❌ ollama create exited with code {process.returncode}")
            return False
        
        except FileNotFoundError:
            print("\n❌ Ollama was not found.")
            print("Make sure Ollama is installed and available in PATH.")
            return False
        
        except Exception as e:
            print(f"\n❌ Update error: {e}")
            return False
    
    try:
        success = await asyncio.wait_for(
            asyncio.to_thread(run_update),
            timeout=300  # 5 minutes
        )
        
        if success:
            print("\n" + "=" * 60)
            print("✅ MODEL UPDATED SUCCESSFULLY")
            print("=" * 60)
            print(f"🤖 Model: {model_name}")
            print("📄 New Modelfile has been applied.")
            print("=" * 60 + "\n")
            return True
        
        print("\n❌ MODEL UPDATE FAILED\n")
        return False
    
    except asyncio.TimeoutError:
        print("\n⏱️ Model update timed out after 5 minutes.")
        return False
    
    except KeyboardInterrupt:
        print("\n⏭️ Model update skipped.")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected update error: {e}")
        return False

# ---------- Run the update on startup ----------
print("\n" + "=" * 50)
print("Checking for Modelfile updates...")
print("=" * 50)

try:
    asyncio.run(update_model_from_modelfile(MODEL))
except KeyboardInterrupt:
    print("\n⏭️  Update skipped by user.")
    # Continue anyway

# ---------- Confirmation loop with masked token ----------
def mask_token(token):
    if len(token) <= 8:
        return token
    return token[:4] + "..." + token[-4:]

while True:
    print("\n" + "=" * 50)
    print(f"Current Discord token: {mask_token(DISCORD_TOKEN)}")
    print(f"Current Ollama model : {MODEL}")
    print(f"Trigger names        : {', '.join(AI_NAME_VARIATIONS) if AI_NAME_VARIATIONS else 'None (only direct mentions)'}")
    print("=" * 50)
    confirm = input("Is this correct? (y/n): ").strip().lower()
    if confirm == 'y':
        break
    elif confirm == 'n':
        print("\nWhat would you like to update?")
        print("  1. Discord token")
        print("  2. Ollama model name")
        print("  3. Trigger names")
        print("  4. Both (token + model)")
        print("  5. All three")
        choice = input("Enter your choice (1/2/3/4/5): ").strip()
        if choice == '1':
            new_token = input("Enter new Discord token: ").strip()
            if new_token:
                DISCORD_TOKEN = new_token
                set_key(".env", "DISCORD_TOKEN", DISCORD_TOKEN)
                os.environ["DISCORD_TOKEN"] = DISCORD_TOKEN
        elif choice == '2':
            new_model = input("Enter new Ollama model name: ").strip()
            if new_model:
                MODEL = new_model
                set_key(".env", "OLLAMA_MODEL", MODEL)
                os.environ["OLLAMA_MODEL"] = MODEL
                asyncio.run(update_model_from_modelfile(MODEL))
        elif choice == '3':
            new_trigger = input("Enter new trigger names (comma-separated): ").strip()
            if new_trigger:
                set_key(".env", "TRIGGER_NAMES", new_trigger)
                os.environ["TRIGGER_NAMES"] = new_trigger
                AI_NAME_VARIATIONS = [name.strip() for name in new_trigger.split(",") if name.strip()]
        elif choice == '4':
            new_token = input("Enter new Discord token: ").strip()
            if new_token:
                DISCORD_TOKEN = new_token
                set_key(".env", "DISCORD_TOKEN", DISCORD_TOKEN)
                os.environ["DISCORD_TOKEN"] = DISCORD_TOKEN
            new_model = input("Enter new Ollama model name: ").strip()
            if new_model:
                MODEL = new_model
                set_key(".env", "OLLAMA_MODEL", MODEL)
                os.environ["OLLAMA_MODEL"] = MODEL
                asyncio.run(update_model_from_modelfile(MODEL))
        elif choice == '5':
            new_token = input("Enter new Discord token: ").strip()
            if new_token:
                DISCORD_TOKEN = new_token
                set_key(".env", "DISCORD_TOKEN", DISCORD_TOKEN)
                os.environ["DISCORD_TOKEN"] = DISCORD_TOKEN
            new_model = input("Enter new Ollama model name: ").strip()
            if new_model:
                MODEL = new_model
                set_key(".env", "OLLAMA_MODEL", MODEL)
                os.environ["OLLAMA_MODEL"] = MODEL
                asyncio.run(update_model_from_modelfile(MODEL))
            new_trigger = input("Enter new trigger names (comma-separated): ").strip()
            if new_trigger:
                set_key(".env", "TRIGGER_NAMES", new_trigger)
                os.environ["TRIGGER_NAMES"] = new_trigger
                AI_NAME_VARIATIONS = [name.strip() for name in new_trigger.split(",") if name.strip()]
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    else:
        print("Please enter 'y' or 'n'.")

# Safety check
if not DISCORD_TOKEN or not MODEL:
    raise ValueError("Token or model missing after confirmation.")

# ---------- Configuration ----------
# AI_NAME_VARIATIONS is already defined above

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)
conversation = {}

# ---------- Helper Functions ----------

def is_talking_to_bot(content):
    content_lower = content.lower().strip()
    # Check if any trigger name appears at the start or as a separate word
    for name in AI_NAME_VARIATIONS:
        name_lower = name.lower()
        if content_lower.startswith(name_lower) or f" {name_lower}" in content_lower:
            return True
    # Also check common question patterns (these are still useful)
    patterns = [
        r"^(hey|yo|hi|hello|sup|what's up|wassup)\s*(bonnie|blue|ai|bot)",  # keep but we might want to remove hardcoded names? Actually these are still hardcoded but they are patterns not trigger names. The user asked to remove trigger words, not patterns. I'll keep patterns but they might still catch "hey bot" etc. If they want to remove all, they can. But they said "delete the words that triggers the bot (like leave it open so the user can enter it themselves)" – the trigger words are the names like "bonnie", "blue". The patterns are more generic, so I'll keep them.
        r"^(bonnie|blue|ai|bot)\s*(can you|could you|would you|will you|do you|are you)",
        r"^(bonnie|blue|ai|bot)[,!\?]",
        r"tell me", r"can you", r"could you", r"would you", r"will you",
        r"do you", r"are you", r"what's", r"what is", r"who is", r"when is",
        r"where is", r"why is", r"how do", r"how to", r"help me", r"i need",
        r"can i", r"should i"
    ]
    for pattern in patterns:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return True
    if content_lower.endswith('?'):
        return True
    return False

async def safe_send(message, content, mention_author=False):
    try:
        await message.reply(content, mention_author=mention_author)
    except (discord.errors.HTTPException, AttributeError):
        try:
            await message.channel.send(content)
        except Exception as e:
            print(f"Failed to send message: {e}")

# ---------- Moderation Commands ----------

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    if amount < 1:
        await ctx.send("Please specify a positive number.")
        return
    if amount > 100:
        await ctx.send("Cannot delete more than 100 messages at once.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted {len(deleted) - 1} messages.", delete_after=5)

@bot.command(name="delete")
@commands.has_permissions(manage_messages=True)
async def delete_message(ctx, message_id: int):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.delete()
        await ctx.send(f"Deleted message from {msg.author.display_name}", delete_after=5)
    except discord.errors.NotFound:
        await ctx.send("Message not found.")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to delete that message.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="edit")
@commands.has_permissions(manage_messages=True)
async def edit_message(ctx, message_id: int, *, new_content: str):
    try:
        msg = await ctx.channel.fetch_message(message_id)
        await msg.edit(content=new_content)
        await ctx.send(f"Edited message from {msg.author.display_name}", delete_after=5)
    except discord.errors.NotFound:
        await ctx.send("Message not found.")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to edit that message.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("You cannot kick yourself.")
        return
    if member == ctx.guild.owner:
        await ctx.send("You cannot kick the server owner.")
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("You cannot kick someone with a higher or equal role.")
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"Kicked {member.display_name} for: {reason}")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to kick that member.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("You cannot ban yourself.")
        return
    if member == ctx.guild.owner:
        await ctx.send("You cannot ban the server owner.")
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("You cannot ban someone with a higher or equal role.")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"Banned {member.display_name} for: {reason}")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to ban that member.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member_name: str):
    banned_users = [entry async for entry in ctx.guild.banned_users()]
    for entry in banned_users:
        if member_name.lower() in entry.user.name.lower():
            try:
                await ctx.guild.unban(entry.user)
                await ctx.send(f"Unbanned {entry.user.display_name}")
                return
            except Exception as e:
                await ctx.send(f"Error unbanning: {e}")
                return
    await ctx.send(f"Could not find banned user: {member_name}")

@bot.command(name="timeout")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: int, *, reason="No reason provided"):
    if member == ctx.author:
        await ctx.send("You cannot timeout yourself.")
        return
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("You cannot timeout someone with a higher or equal role.")
        return
    try:
        timeout_duration = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        await member.timeout(timeout_duration, reason=reason)
        await ctx.send(f"Timed out {member.display_name} for {duration} minutes. Reason: {reason}")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to timeout that member.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="untimeout")
@commands.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    try:
        await member.timeout(None, reason="Timeout removed")
        await ctx.send(f"Removed timeout from {member.display_name}")
    except discord.errors.Forbidden:
        await ctx.send("I don't have permission to remove timeout from that member.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="warn")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    embed = discord.Embed(
        title="⚠️ Warning",
        description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** {reason}",
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    warning_channel = discord.utils.get(ctx.guild.channels, name="warnings")
    if warning_channel:
        await warning_channel.send(embed=embed)
    else:
        await ctx.send(embed=embed)
    try:
        await member.send(f"You have been warned in {ctx.guild.name} for: {reason}")
    except:
        pass
    await ctx.send(f"Warned {member.display_name} for: {reason}")

@bot.command(name="slowmode")
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, seconds: int):
    if seconds < 0:
        await ctx.send("Slowmode cannot be negative.")
        return
    if seconds > 21600:
        await ctx.send("Slowmode cannot exceed 6 hours (21600 seconds).")
        return
    try:
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await ctx.send("Slowmode disabled.")
        else:
            await ctx.send(f"Slowmode set to {seconds} seconds.")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔒 Channel locked by {ctx.author.mention}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    try:
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        await ctx.send(f"🔓 Channel unlocked by {ctx.author.mention}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="userinfo")
async def userinfo(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(
        title=f"User Info: {member.display_name}",
        color=member.color or discord.Color.blue()
    )
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Status", value=str(member.status), inline=True)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]) or "None", inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="serverinfo")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"Server Info: {guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# ---------- Error Handling ----------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"You don't have permission. Missing: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: {error.param.name}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument: {error}")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Command error: {error}")

# ---------- Main Bot Events ----------
@bot.event
async def on_ready():
    print("\n╔══════════════════════════════════════════════════╗")
    print("║       BOT IS ONLINE (BETA VERSION)             ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"Logged in as {bot.user}")
    print(f"Server Members Intent: {bot.intents.members}")
    print(f"Presences Intent: {bot.intents.presences}")
    print(f"Moderation Intent: {bot.intents.moderation}")
    print(f"Using local Ollama model: {MODEL}")
    print(f"Trigger names: {', '.join(AI_NAME_VARIATIONS) if AI_NAME_VARIATIONS else 'None (only direct mentions)'}")
    print("Bot will respond in any channel where it has permission.")
    print("Bot is ready! (Use Ctrl+C to stop)\n")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id

    if user_id not in conversation:
        conversation[user_id] = []

    mentioned = bot.user in message.mentions
    is_directed = mentioned or is_talking_to_bot(message.content)

    clean_content = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()

    if not is_directed:
        await bot.process_commands(message)
        return

    # No server context – just the user's cleaned message
    user_content = clean_content

    conversation[user_id].append({"role": "user", "content": user_content})

    messages_for_ai = conversation[user_id]

    async with message.channel.typing():
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=MODEL,
                messages=messages_for_ai
            )
            reply = response.choices[0].message.content
            conversation[user_id].append({"role": "assistant", "content": reply})

            if len(reply) > 2000:
                for i in range(0, len(reply), 2000):
                    await safe_send(message, reply[i:i+2000])
            else:
                await safe_send(message, reply)

        except Exception as e:
            print(f"Error: {e}")
            await safe_send(message, "Sorry, I encountered an error.")

    await bot.process_commands(message)

# ---------- Start the bot ----------
bot.run(DISCORD_TOKEN)