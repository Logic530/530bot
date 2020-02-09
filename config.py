from nonebot.default_config import *


# 设置主机和端口
HOST = '127.0.0.1'
PORT = 2333

# 设置超级用户QQ号，可迭代对象
SUPERUSERS = {
    604853511
}

# 设置命令起始，可迭代对象
COMMAND_START = {
    '$'
}

# 设置命令分隔，命令会被解析为元组
# note.add -> ('note', 'add')
COMMAND_SEP = {
    '.'
}