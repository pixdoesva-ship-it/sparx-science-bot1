import discord
from discord.ext import commands
import asyncio
import os
from openai import AsyncOpenAI
from playwright.async_api import async_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Sparx Science Bot is online as {bot.user}")

@bot.command(name="do_science")
async def do_science(ctx, username: str, password: str, school_name: str, question_amount: int = 20):
    msg = await ctx.send(f"🔬 Logging into **Sparx Science** as **{username}**...\nTarget: {question_amount} questions")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            page = await browser.new_page()

            # Login
            await page.goto("https://selectschool.sparx-learning.com/")
            await page.fill("#school-search-input", school_name)
            await page.press("#school-search-input", "Enter")
            await page.click(".school-result")

            await page.fill('[name="username"]', username)
            await page.fill('[name="password"]', password)
            await page.press('[name="password"]', "Enter")

            await page.wait_for_url("**sparxscience**", timeout=60000)
            await msg.edit(content="✅ Logged in! Starting to answer questions...")

            answered = 0
            while answered < question_amount:
                question_text = await page.inner_text(".question-text, .question-container", timeout=15000)

                # Real AI answer
                response = await client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "Answer with only the letter A, B, C or D."},
                              {"role": "user", "content": question_text}],
                    temperature=0.0,
                    max_tokens=5
                )
                answer_letter = response.choices[0].message.content.strip().upper()[0]

                await page.click(f"text={answer_letter}", timeout=10000)

                answered += 1
                await msg.edit(content=f"🔬 Answered {answered}/{question_amount} questions...")

                await asyncio.sleep(5)

            await msg.edit(content=f"🎉 **COMPLETE!** Finished {question_amount} Sparx Science questions for **{username}**!")
            await browser.close()

    except Exception as e:
        await msg.edit(content=f"❌ Error: {str(e)[:700]}")

bot.run(BOT_TOKEN)
