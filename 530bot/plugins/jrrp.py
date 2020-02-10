from nonebot import on_command, CommandSession
import datetime
import random

@on_command('jrrp')
async def jrrp(session: CommandSession):
    user_id = session.ctx['user_id']
    date = str(datetime.date.today())

    random.seed(str(user_id) + date)
    rp = random.randint(1, 100)
    
    await session.send(session.ctx['sender']['nickname'] + ' 今天的人品是 ' + str(rp))