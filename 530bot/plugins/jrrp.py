from nonebot import on_command, CommandSession
import datetime
import random

@on_command('jrrp')
async def jrrp(session: CommandSession):
    user_id = session.ctx['user_id']
    nickname = session.ctx['sender']['nickname']
    date = str(datetime.date.today())

    random.seed(str(user_id) + date)
    rp = random.randint(1, 100)

    if rp == 1:
        message = 'QAQ ' + nickname + ' 今天的人品是……' + str(rp)
        pass
    if rp in range(2, 40):
        message = nickname + ' 今天的人品是 ' + str(rp) + ' 不要灰心丧气啊'
        pass
    if rp in range(40, 60):
        message = nickname + ' 今天的人品是 ' + str(rp) + ' 还不错啦'
        pass
    if rp in range(60, 80):
        message = nickname + ' 今天的人品是 ' + str(rp) + ' 似乎运气很好呢'
        pass
    if rp in range(80, 100):
        message = nickname + ' 今天的人品是 ' + str(rp) + ' 人品爆棚呢'
        pass
    if rp == 100:
        message = nickname + ' 今天的人品居然是…………' + str(rp)
        pass

    await session.send(message)