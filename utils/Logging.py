from datetime import datetime
from zoneinfo import ZoneInfo

import logging  # 采用logging来替换所有print
from logging.handlers import TimedRotatingFileHandler
from khl import Message,PrivateMessage
from os import getpid

LOGGER_NAME = "botlog"
LOGGER_FILE = "./log/bot.log"  # 如果想修改log文件的名字和路径，修改此变量
LOGGER_BOT_PID = getpid() # 机器人pid


def beijing(sec, what):
    """日志时间返回北京时间"""
    beijing_time = datetime.now(ZoneInfo('Asia/Shanghai'))  # 返回北京时间
    return beijing_time.timetuple()


# 日志时间改为北京时间
logging.Formatter.converter = beijing  # type: ignore

# 只打印info以上的日志（debug低于info）
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
# 获取一个logger对象
_log = logging.getLogger(LOGGER_NAME)
"""自定义的logger对象"""
# 实例化控制台handler和文件handler，同时输出到控制台和文件
# cmd_handler = logging.StreamHandler() # 默认设置里面，就会往控制台打印信息;自己又加一个，导致打印俩次
file_handler = logging.FileHandler(LOGGER_FILE, mode="a", encoding="utf-8")
fmt = logging.Formatter(fmt="[%(asctime)s] [%(bot_pid)d] %(levelname)s:%(filename)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt="%y-%m-%d %H:%M:%S")
file_handler.setFormatter(fmt)
# 每3天新生成一个
log_handler = TimedRotatingFileHandler(LOGGER_FILE, when='D',interval=3)
log_handler.setFormatter(fmt)

# _log.addHandler(file_handler)
_log.addHandler(log_handler)
_log = logging.LoggerAdapter(_log, {"bot_pid": LOGGER_BOT_PID})
_log.info(f"[INIT] init bot logging object, PID:{LOGGER_BOT_PID}")


def log_msg(msg:Message):
    """命令日志"""
    try:
        gid,chid = "pm","pm"
        if not isinstance(msg, PrivateMessage): # 不是私聊
            chid = msg.ctx.channel.id
            gid = msg.ctx.guild.id
        # 打印日志
        _log.info(
            f"G:{gid} | C:{chid} | Au:{msg.author_id} {msg.author.username}#{msg.author.identify_num} = {msg.content}"
        )
    except Exception as result:
        _log.exception(f"err in logging")
