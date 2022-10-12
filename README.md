# Kook-OnlineUser-Bot
A Online-User Checking Bot for KOOK (khl.py)

一个可以显示当前KOOK服务器`在线/总人数`的bot

## 如何使用
目前在线/总人数小助手支持的指令如下
* `/alive` 看看bot是否在线
* `/svck` 查看当前服务器的在线/总人数
* `/adck 频道id '前缀' '后缀'` 设置在本服务器的在线人数更新。
    
    默认格式为`频道在线 10/100`。其中`频道在线 `为前缀，默认后缀为空。可以手动指定前缀和后缀，来适应你的频道的命名风格。记得加**英文的引号**来保证前缀/后缀的完整性！
* 在线人数监看设定为**30分钟**更新一次，使用示例如下：
    
    ```
    /adck 111111111111 "频道在线 | " " 测试ing"
    ```
* `/tdck` 取消本服务器的在线人数监看\n" 


## 依赖项
保证你的python版本高于3.7，安装下面的包
```
pip install khl.py
```

框架基于[khl.py](https://github.com/TWT233/khl.py/tree/main/example)，使用`aiohttp`来调用kook官方的api，对频道进行编辑。

> aiohttp已在khl.py中包含，无需手动下载

关于code里面的makefile，这是用于linux下快速启动bot后台运行的。如果你想在自己的linux服务器使用，请把里面的`py3`改成你自己云服务器上的python（就是用来命令行运行python程序的哪一个，如`python3`）