import json
from khl import Bot, Cert
from ..Logging import _log
from .FileManage import FileManage, save_all_file

# 配置机器人
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

config = FileManage("./config/config.json", True)
"""配置文件"""
SVdict = FileManage("./log/server.json")
"""数据监控记录文件"""
LAdict = FileManage("./log/yesterday.json")
"""昨日新增用户配置文件"""

BotToken = config['token']
"""机器人token"""
bot = Bot(token=BotToken) 
"""main bot"""

# 如果配置文件要求使用webhook，则重新初始化
if not config['ws']:
    _log.info(f"[BOT] using webhook at port:{config['webhook_port']}")
    bot = Bot(cert=Cert(token=config['token'],
                        verify_token=config['verify_token'],
                        encrypt_key=config['encrypt']),
              port=config['webhook_port'])  # webhook

_log.info(f"[BOT] bot object init success.")
