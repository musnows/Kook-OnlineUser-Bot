# encoding: utf-8
# 本文件仅供replit部署使用，具体请看如下文档
# 如果您是在云服务器/本地电脑部署本bot，请忽略此文件

from flask import Flask
from threading import Thread
from onbot import bot, log_dup, GetTime, config
# 初始化
app = Flask(' ')


# 设立根路径作为api调用
@app.route('/')
def home():
    text = f"[{GetTime()}] request | bot online!"
    print(text)
    return text


# 开始运行，绑定ip和端口
def run():
    app.run(host='0.0.0.0', port=8000)


# 通过线程运行
def keep_alive():
    print(f"[flask] start at {GetTime()}")
    t = Thread(target=run)
    t.start()


if __name__ == '__main__':
    print(f"[Start.Replit] at [%s]" % GetTime())
    # 设置输出重定向
    log_dup('./log/log.txt')
    # 再打印一次到重定向后的文件中
    print(f"[Start.Replit] logdup at [%s]" % GetTime())
    # 如果是使用websocket，则启用这个
    if config['ws']:
        keep_alive() # 按线程运行
    bot.run()
