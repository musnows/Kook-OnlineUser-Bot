import time

def get_time():  #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


def get_date():  #将获取当前日期成函数方便使用
    return time.strftime("%y-%m-%d", time.localtime())