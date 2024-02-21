import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guild_messages = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

existing_tickets = {}  # ユーザーごとの既存のチケットを格納する辞書
deleted_tickets = set()  # 削除されたチケットの内容を格納するセット

@bot.hybrid_command(name="ticket-add")
async def ticket(ctx, *, issue: str):
    user_id = ctx.author.id
    if issue in deleted_tickets:
        deleted_tickets.remove(issue)  # 削除されたチケットのセットから削除する

    category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if category is None:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True)
        }
        category = await ctx.guild.create_category(name="Tickets", overwrites=overwrites)

    ticket_channel_name = issue[:50]  # チケットの内容から最初の50文字をチャンネル名に使用
    existing_channel = discord.utils.get(ctx.guild.text_channels, name=ticket_channel_name)
    if existing_channel:
        await ctx.send("すでにチケットが作成されています。")
        return

    channel = await category.create_text_channel(name=ticket_channel_name)
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)

    embed = discord.Embed(title="新しいチケットが作成されました", description=f"問題: {issue}", color=discord.Color.green())
    embed.add_field(name="チケット作成者", value=ctx.author.mention, inline=False)
    embed.add_field(name="チケットチャンネル", value=channel.mention, inline=False)
    message = await channel.send(embed=embed)
    await ctx.send("チケットが正常に作成されました！")
    existing_tickets[user_id] = issue
    await message.add_reaction("🔒")

@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    if payload.emoji.name == "🔒":
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author == bot.user:
            # 削除されたチケットの内容を記録
            issue = message.embeds[0].description.split(': ')[1]  # チケットの内容を取得
            deleted_tickets.add(issue)  # 削除されたチケットの内容をセットに追加
            await channel.delete()

@ticket.error
async def ticket_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("チケットの内容を提供してください。例: `!ticket サーバーがダウンしています`")

bot.run("MTE5MDQ3NTkyODg2MjcyNDI4OA.G7nFxB.FBC_9pauOIJSYgog5yoc-sLpvBmbzHM8XMGQIU")
