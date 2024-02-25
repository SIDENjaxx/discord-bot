"""Module providing a function printing python version."""
import asyncio
import heapq
import datetime
from discord.ext import commands
import discord





bot = commands.Bot(command_prefix = ("!"), intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'起動完了:{bot.user}')
    bot.loop.create_task(check_scheduled_messages())


# 運営ロールをチェックするカスタムチェック関数
def is_admin(ctx):
    # もしメッセージを送信したメンバーが運営ロールを持っている場合はTrueを返します
    return any(role.name == '運営' for role in ctx.author.roles)


# 予約メッセージを管理する辞書
scheduled_messages = []

@bot.hybrid_command(name="schedule")
@commands.check(is_admin)
async def schedule(ctx, year: int, month: int, day: int, hour: int, minute: int, channel: discord.TextChannel, *, content):
    """指定した時間にメッセージを送信できる (運営のみ)"""
    try:
        date_time = datetime.datetime(year, month, day, hour, minute)
    except ValueError:
        await ctx.send('日時を正しい形式で指定してください。例: !schedule 2024 1 31 12 00 #channel 予約メッセージ内容')
        return

    if date_time <= datetime.datetime.now():
        await ctx.send('過去の日時は予約できません。')
        return

    heapq.heappush(scheduled_messages, (date_time, channel.id, content))
    await ctx.send('予約メッセージを登録しました。')

async def check_scheduled_messages():
    await bot.wait_until_ready()
    while not bot.is_closed():
        while scheduled_messages and scheduled_messages[0][0] <= datetime.datetime.now():
            date_time, channel_id, content = heapq.heappop(scheduled_messages)
            channel = bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(content)
                except discord.Forbidden:
                    print(f"メッセージを送信できません: {content}")
            else:
                print(f"チャンネルが見つかりません: {channel_id}")
        await asyncio.sleep(max(1, (scheduled_messages[0][0] - datetime.datetime.now()).total_seconds() if scheduled_messages else 10))

@schedule.error
async def schedule_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("このコマンドを実行する権限がありません。運営ロールが必要です。")



bot.run("TOKEN")