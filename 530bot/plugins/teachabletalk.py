from nonebot import (CommandGroup, CommandSession, NLPSession, logger,
                     on_command, on_natural_language, permission)
import sqlite3
import re
from random import choice
from hashlib import md5

# talk命令组
talk = CommandGroup('talk', shell_like=True)

# TODO 自动配置数据库

# 连接数据库
database = sqlite3.connect('./teachabletalk.sqlite')
cursor = database.cursor()


def rule_exist(pattern: str, reply: str):
    check_SQL = '''SELECT * FROM rules WHERE pattern = ? AND reply = ?'''
    cursor.execute(check_SQL, (pattern, reply))
    if cursor.fetchone():
        return True
    else:
        return False


def add_rule(pattern: str, reply: str):
    if rule_exist(pattern, reply):
        raise sqlite3.IntegrityError
    add_SQL = '''INSERT INTO rules (pattern, reply) VALUES (?, ?)'''
    cursor.execute(add_SQL, (pattern, reply))
    database.commit()


def del_rule(pattern: str, reply: str):
    if not rule_exist(pattern, reply):
        raise Exception
    del_rule_SQL = '''DELETE FROM rules WHERE pattern = ? AND reply = ?'''
    cursor.execute(del_rule_SQL, (pattern, reply))
    database.commit()


def search_rule(keyword: str):
    search_SQL = '''SELECT * FROM rules WHERE pattern LIKE ? OR reply LIKE ?'''
    cursor.execute(search_SQL, (keyword, keyword))
    return cursor.fetchall()


def add_blacklist(id: int):
    add_blacklist_SQL = '''INSERT INTO blacklist (id) VALUES (?)'''
    cursor.execute(add_blacklist_SQL, (id,))
    database.commit()

# 子命令add，用于添加规则
@talk.command('add', only_to_me=False)
async def talk_add(session: CommandSession):
    logger.debug('执行添加命令')
    args = session.args['argv']
    try:
        assert len(args) == 2
        pattern = args[0]
        reply = args[1]
    except AssertionError:
        await session.send('参数错了呢~')
        return

    try:
        add_rule(pattern, reply)
    except sqlite3.IntegrityError:
        await session.send('好像之前添加过了')
        return
    rule_md5 = md5((pattern + reply).encode())
    await session.send('我知道啦' + ' 记忆条目已更新 ' + rule_md5.hexdigest())


# 子命令del，用于删除规则
@talk.command('del', only_to_me=False)
async def talk_del(session: CommandSession):
    logger.debug('执行删除命令')
    args = session.args['argv']
    try:
        assert len(args) == 2
        pattern = args[0]
        reply = args[1]
    except AssertionError:
        session.send('参数错了呢~')

    try:
        del_rule(pattern, reply=reply)
    except Exception:
        await session.send('你说的这个我没有听说过呢')
        return
    await session.send('好吧好吧，删除这一条' + ' ' + pattern + ' ' + reply)

# 黑名单指令，用于添加黑名单
@talk.command('blacklist', only_to_me=False, permission=permission.SUPERUSER)
async def blacklist(session: CommandSession):
    logger.debug('执行添加黑名单指令')
    args = session.args['argv']

    try:
        assert len(args) == 1
        id = int(args[0])
    except (AssertionError, ValueError):
        await session.send('参数错了呢~')
        return
    try:
        add_blacklist(id)
    except sqlite3.IntegrityError:
        session.send('是这个人吗？ ' + str(id) + ' 之前说过啦')
        return
    await session.send('原来 ' + str(id) + ' 是坏人吗，不听ta说话了')

'''
# 子命令search，用于搜索规则
@talk.command('search')
async def talk_search(session: CommandSession):
    logger.debug('执行搜索命令')
    try:
        assert len(session.args['argv']) in (1, 2)
    except AssertionError:
        session.send('参数错了呢~')
'''

# 自然语言处理，用于执行自动回复
@on_natural_language(only_to_me=False)
async def _(session: NLPSession):

    # 检查用户是否在黑名单
    get_blacklist_SQL = '''SELECT * from blacklist'''
    cursor.execute(get_blacklist_SQL)
    blacklist = cursor.fetchall()
    if session.ctx['user_id'] in blacklist:
        logger.debug('用户在黑名单中，忽略')
        return

    cursor.execute('''SELECT * FROM rules''')
    rules = cursor.fetchall()
    message = session.msg_text
    if not message:
        return
    reply_list = []

    for rule in rules:
        pattern = rule[1]
        reply = rule[2]
        if re.match(message, pattern) or pattern in message:
            reply_list.append(reply)
        pass

    if reply_list:
        await session.send(choice(reply_list))
    else:
        logger.debug('没有匹配的规则，忽略')
