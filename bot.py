import os
from dotenv import load_dotenv
import random

import discord
from discord.ext import commands

from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker

from datetime import date, time, datetime, timedelta

from models import *

engine = create_engine('sqlite:///kantor-bot.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# If table doesn't exist, create the database
if not engine.has_table('workdays'):
    Base.metadata.create_all(engine)

load_dotenv(override=True)
token = os.getenv('BOT_TOKEN')

description = "A nice little office assistant bot"
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), description=description)

# Definisikan format string untuk tanggal dan waktu
date_format = '%Y-%m-%d'
time_format = '%H:%M'

# jam kerja
delta = timedelta(hours=+6) 

@bot.event
async def on_ready():
    print('Logged in as {0.user.name} with id {0.user.id}'.format(bot))
    print('-----------------')
    print('ready for action!')

    bot.workday_id = None

@bot.event
async def on_command_error(ctx, error):
    await ctx.send('''Ups, ada kesalahan: {}'''.format(error))

@bot.command(name='ping')
async def ping(ctx):
    '''Returns pong when called'''
    author = ctx.author
    guild = ctx.guild
    await ctx.send('Pong for {} from {}'.format(author.id,guild))

@bot.command(name='getworkdayid')
async def getworkdayid(ctx):
    await ctx.send(bot.workday_id)

@bot.command(name='selfroles')
async def selfroles(ctx):
    await ctx.send(ctx.author.roles)

@bot.command(name='masuk')
async def masuk(ctx, waktu='sekarang'):
    '''Catat waktu masuk pengurus'''

    # Kalau bukan pengurus, fungsi ini gak berlaku
    """ if 'Pengurus' not in ctx.author.roles:
        await ctx.send('Maaf, antum nggak bisa pakai fungsi ini')
        return """
    
    day = datetime.now()

    workday_date = day.strftime(date_format)
    jam_pulang = day + delta

    masuk_messages = [
        'Siap, brader {}. Presensi antum udah kecatet.',
        'Woke, Akh {}. Semangat pagi 🔥',
        'Noted, bro {}. Selamat dataaaang 💐',
        'Siap. Pagi semangat Mas {} 🌞',
        'Aku siap, aku siap, aku siap. Selamat pagi, bro {}. Pagi yang cerah bukan? 🌈 '
        'Tafadhdhal, Akh {}. Gak lupa mandi 🧼 kan? Wkwkwk'
    ]

    try:
        member = session.query(Member).filter(Member.discord_id == ctx.author.id).first()
        workday_existed = session.query(Workday).filter(Workday.date == workday_date).first()

        # Hari kerja ini apakah pernah terdaftar?
        if workday_existed:
            bot.workday_id = workday_existed.id
        else:
            workday = Workday(date=day.date())
            session.add(workday)
            session.commit()
            bot.workday_id = workday.id

        # Member pernah kedaftar?
        if not member:
            member = Member(name=ctx.author.name, discord_id=ctx.author.id)
            session.add(member)
        
        # Udah ngisi presensi hari ini?
        attended = session.query(Attendance).filter(Attendance.workday_id == bot.workday_id and Attendance.member_id == member.id).count()

        if attended > 0 :
            await ctx.send('Antum udah presensi hari ini, brader {}'.format(ctx.author.mention))
            return 
        else:
            attending = Attendance(workday_id = bot.workday_id, member_id = member.id, masuk = 1, waktu_masuk = day.time())
            session.add(attending)

            session.commit()

            await ctx.send(random.choice(masuk_messages).format(ctx.author.mention))
            await ctx.send('Jam pulang ideal antum adalah {} 👌 {}'.format(jam_pulang.strftime(time_format), ctx.author.mention))

    except Exception as e:
        await ctx.send('Ugghh, terjadi error, bung!:')
        await ctx.send(e)

@bot.command(name='on')
async def on_masuk(ctx):
    await masuk(ctx)

@bot.command(name='kdr')
async def kdr(ctx):
    await masuk(ctx)

@bot.command(name='pulang')
async def pulang(ctx):
    member = session.query(Member).filter(Member.discord_id == ctx.author.id).first()
    now = datetime.now()

    attendance = session.query(Attendance).filter(Attendance.workday_id == bot.workday_id and Attendance.member_id == member.id).first()

    attendance.waktu_pulang = now.time()

    session.add(attendance)
    session.commit()

    pulang_messages = [
        'Siap bro {} 👌, hati-hati di jalan. 👋 ',
        'Baik, akhi {}. Jazakumullahu khairan buat hari ini ya.',
        'Noted 📝. Jumpa lagi esok. Selamat istirahat brader {} ♻️ .',
        'Oke siap, akh {}. Makasih atas karya hari ini 👍, gak sabar nunggu hari kreatif dengan antum lagi.',
        'Bip bop bip bop. Matur nuwun untuk hari ini 🙏, Mas {}.',
        'Siap brader {}. Jazakumullahu khairan ya 👌.',
        'Hari yang menyenangkan, jumpa lagi bro {} 👋'
    ]

    await ctx.send(random.choice(pulang_messages).format(ctx.author.mention))

# Buat ngetes aja
@bot.command(name='minum')
async def minum(ctx):
    channel = ctx.channel

    options = {
        '1': 'Kopi',
        '2': 'Susu',
        '3': 'Teh'
    }

    await ctx.send("""
    Mau minum apa?
    1. Kopi
    2. Susu
    3. Teh
                """)

    def check(m):
        return m.channel == channel and m.author != bot.user
    
    msg = await bot.wait_for('message', check=check)
    await ctx.send('Oke {.author.name}!'.format(msg))


# Run the bot
if __name__ == '__main__':
    try:
        bot.run(token)
    except Exception as e:
        print('Could not start Bot')
        print(e)
    finally:
        print('clossing Session')
        session.close()