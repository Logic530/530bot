from nonebot import (CommandGroup, CommandSession, NLPSession, logger,
                     on_command, on_natural_language, permission)
import sqlite3
import re
from random import choice

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
        await session.send('参数错误')
        return

    try:
        add_rule(pattern, reply)
    except sqlite3.IntegrityError:
        await session.send('规则已存在')
        return
    await session.send('规则已添加' + ' ' + pattern + ' ' + reply)


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
        session.send('参数错误')

    try:
        del_rule(pattern, reply=reply)
    except Exception:
        await session.send('要删除的记录不存在')
        return
    await session.send('规则删除成功' + ' ' + pattern + ' ' + reply)

# 黑名单指令，用于添加黑名单
@talk.command('blacklist', only_to_me=False, permission=permission.SUPERUSER)
async def blacklist(session: CommandSession):
    logger.debug('执行添加黑名单指令')
    args = session.args['argv']

    try:
        assert len(args) == 1
        id = int(args[0])
    except (AssertionError, ValueError):
        await session.send('参数错误')
        return

    add_blacklist(id)
    await session.send('黑名单已添加' + ' ' + str(id))

'''
# 子命令search，用于搜索规则
@talk.command('search')
async def talk_search(session: CommandSession):
    logger.debug('执行搜索命令')
    try:
        assert len(session.args['argv']) in (1, 2)
    except AssertionError:
        session.send('参数错误')
'''

# 自然语言处理，用于执行自动回复
@on_natural_language(only_to_me=False)
async def _(session: NLPSession):

    # 检查用户是否在黑名单
    get_blacklist_SQL = '''SELECT * from blacklist'''
    cursor.execute(get_blacklist_SQL)
    blacklist = cursor.fetchall()
    if session.ctx['user_id'] in blacklist:
        return

    cursor.execute('''SELECT * FROM rules''')
    rules = cursor.fetchall()
    message = session.msg_text
    reply_list = []

    for rule in rules:
        pattern = rule[1]
        reply = rule[2]
        if re.match(message, pattern) or pattern in message:
            reply_list.append(reply)
        pass

    if reply_list:
        await session.send(choice(reply_list))
