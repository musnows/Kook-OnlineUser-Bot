# encoding: utf-8:
import os
import json
import time
import copy
import aiohttp
import traceback
import sys

from khl import Bot, Message, Cert, EventTypes, Channel,PrivateMessage
from khl.card import CardMessage, Card, Module, Element, Types

# 配置机器人
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 预加载服务器在线人数监看
with open("./log/server.json", 'r', encoding='utf-8') as frsv:
    SVdict = json.load(frsv)
# 预加载昨日新增用户监看
with open("./log/yesterday.json", 'r', encoding='utf-8') as frla:
    LAdict = json.load(frla)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])  # websocket
"""main bot"""
if not config['ws']:
    print(f"[BOT] using webhook at port:{config['webhook_port']}")
    bot = Bot(cert=Cert(token=config['token'],
                        verify_token=config['verify_token'],
                        encrypt_key=config['encrypt']),
              port=config['webhook_port'])  # webhook

Botoken = config['token']
"""机器人token"""
kook_base_url = "https://www.kookapp.cn"
"""kook api基础url"""
kook_headers = {f'Authorization': f"Bot {Botoken}"}
"""kook api基础kook_headers"""
debug_ch: Channel
"""日志频道"""


# 向botmarket通信,如果你的机器人没有在bm上线，请删除or注释本task
@bot.task.add_interval(minutes=20)
async def botmarket():
    api = "http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid': '8b3b4c14-d20c-4a23-9c71-da4643b50262'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)
    log_flush()


#############################################################################################


def GetTime():  #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())


def GetDate():  #将获取当前日期成函数方便使用
    return time.strftime("%y-%m-%d", time.localtime())


def log_dup(path: str = './log/log.txt'):
  """设置日志文件的重定向"""
  file = open(path, 'a')
  sys.stdout = file
  sys.stderr = file

def log_flush():
  """刷新缓冲区"""
  sys.stdout.flush()  # 刷新缓冲区
  sys.stderr.flush()  # 刷新缓冲区

def logging(msg: Message):
    """# 在控制台打印msg内容，用作日志"""
    now_time = GetTime()
    guild_id,ch_id = "pm","pm"
    if not isinstance(msg,PrivateMessage):
        guild_id = msg.ctx.guild.id
        ch_id = msg.ctx.channel.id
    print(
        f"[{now_time}] G:{guild_id} - C:{ch_id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}"
    )
    log_flush()


# 查看bot状态
@bot.command(name='alive', case_sensitive=False)
async def alive_check(msg: Message, *arg):
    logging(msg)
    await msg.reply(f"bot alive here")


# 帮助命令
@bot.command(name='CKhelp', case_sensitive=False)
async def help(msg: Message):
    logging(msg)
    cm = CardMessage()
    c3 = Card(
        Module.Header('目前在线/总人数小助手支持的指令如下'),
        Module.Context(
            Element.Text(
                "由muxue开发，开源代码见 [Github](https://github.com/musnows/Kook-OnlineUser-Bot)",
                Types.Text.KMD)))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    c3.append(Module.Header('服务器在线/总人数监看'))
    help_Str1 = "`/alive` 看看bot是否在线\n"
    help_Str1 += "`/svck` 查看当前服务器的在线/总人数\n"
    help_Str1 += "`/adsv1 '前缀' '后缀'` 在当前频道设置本服务器的在线人数更新\n"
    help_Str1 += "`/adsv2 频道id '前缀' '后缀' ` 在指定频道设置本服务器的在线人数更新\n"
    c3.append(Module.Section(Element.Text(help_Str1, Types.Text.KMD)))
    c3.append(
        Module.Section(
            Element.Text("```\n频道/分组id获取：打开`设置-高级-开发者模式`，右键频道复制id\n```",
                         Types.Text.KMD)))
    help_Str2 = "注意`频道id`参数不是`频道名字`！上方有提示\n默认格式为`频道在线 10/100`。其中`频道在线 `为前缀，默认后缀为`空`。可以手动指定前缀和后缀，来适应你的频道的命名风格。记得加**英文的引号**来保证前缀/后缀的完整性！示例:\n```\n/adsv 0000000 \"频道在线 | \" \" 测试ing\"\n```\n"
    help_Str2 += "在线人数监看设定为30分钟更新一次\n"
    help_Str2 += "`/tdsv` 取消本服务器的在线人数监看\n"
    c3.append(Module.Section(Element.Text(help_Str2, Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header('服务器昨日新增用户追踪'))
    help_Str3 = "`/adld` 在当前服务器开启`昨日新增用户`追踪器；\n"
    help_Str3 += "`/adld 1`会设置定时任务，每日00:00向`当前频道`发送昨日新增用户的数量\n"
    help_Str3 += "`/adld 2`则会向当前频道发送消息的同时，更新频道名字\n"
    help_Str3 += "`/ldck` 手动查看本服务器的昨日新增用户数量\n"
    help_Str3 += "`/tdld` 关闭本服务器的`昨日新增用户`追踪器\n"
    help_Str3 += "`昨日新增用户`追踪器更新文字说明：格式为 `10↑ (20↑)`，其中第一个数字为昨日新增用户的数量，第二个数字是相比前天，用户增长的变动"
    c3.append(Module.Section(Element.Text(help_Str3, Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(
        Module.Section(
            '有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    await msg.reply(cm)


# 获取服务器用户数量用于更新
async def server_status(Gulid_ID: str):
    url = kook_base_url + "/api/v3/guild/user-list"
    params = {"guild_id": Gulid_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,
                               headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            #print(ret1)
            return ret1


# 更新频道名字
async def channel_update(channel_id: str, name: str):
    url = kook_base_url + "/api/v3/channel/update"
    params = {"channel_id": channel_id, "name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,
                                headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            print(f"[Option 2] Update_ch:{ret1['message']} - ch:{channel_id}")


# 保存文件
async def file_save(path: str, value):
    with open(path, 'w', encoding='utf-8') as fw1:
        json.dump(value, fw1, indent=2, sort_keys=True, ensure_ascii=False)


#######################################服务器昨日新增用户数量###############################################


#设置监看并在指定频道发送信息
@bot.command(name='adld', case_sensitive=False)
async def Add_YUI_ck(msg: Message, op: int = 0, *arg):
    logging(msg)
    if op < 0 or op > 2:
        await msg.reply(f"选项参数错误，目前只支持 \n0:不推送信息\n1:在本频道推送信息\n2:推送信息的同时修改本频道名")
        return
    if arg != ():
        await msg.reply(f"多余参数，目前只支持 \n0:不推送信息\n1:在本频道推送信息\n2:推送信息的同时修改本频道名")
        return

    try:
        global LAdict

        flag_op = 0
        flag_sv = 0
        guild_id = msg.ctx.guild.id  # 服务器id
        channel_id = msg.ctx.channel.id  # 频道id
        if guild_id in LAdict:
            flag_sv = 1  # 服务器在
            LAdict[guild_id]['channel'] = channel_id  # 更新频道
            if LAdict[guild_id]['option'] != op:
                flag_op = 1  #选项不同
                LAdict[guild_id]['option'] = op  # 更新
        else:
            LAdict[guild_id] = {
                'channel': msg.ctx.channel.id,
                'option': op,
                'date': GetDate(),
                'user_total': 0,
                'increase': 0
            }
            print(f"[adld] new LAdict[{guild_id}]")

        if flag_sv:
            if flag_op:
                if op == 1:
                    await msg.reply(f"已在本频道开启`昨日新增用户`的提醒信息推送！")
                elif op == 2:
                    await msg.reply(
                        f"已在本频道开启`昨日新增用户`的提醒信息推送！bot同时会更新本频道名称为 `📈：昨日变动 变动人数`\n"
                    )
                elif op == 0:
                    await msg.reply(
                        f"已关闭本频道的`昨日新增用户`的提醒信息推送！\n- 追踪仍在进行，您可以用`/ldck`功能手动查看昨日新增\n或用`/tdld`功能关闭本服务器的新增用户追踪器"
                    )
            else:
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启，请勿重复操作")
        else:
            # 获取当前服务器总人数，作为下次更新依据
            ret = await server_status(guild_id)
            LAdict[guild_id]['user_total'] = ret['data']['user_count']
            if op == 0:
                await msg.reply(
                    f"本服务器`昨日新增用户`追踪器已开启！\n- 您没有设置第二个参数，bot不会自动发送推送信息。可在明日用`/ldck`手动查看昨日新增，或重新操作本指令\n- 若需要在本频道开启信息推送，需要添加第二个非零数字作为参数：`/adld 1`"
                )
            elif op == 1:
                await msg.reply(
                    f"本服务器`昨日新增用户`追踪器已开启！\n- 您设置了第二个参数`1`，bot会在每天的00:00向当前频道发送昨日用户数量变动信息\n"
                )
            elif op == 2:
                await msg.reply(
                    f"本服务器`昨日新增用户`追踪器已开启！\n- 您设置了第二个参数`2`，bot会在每天的00:00向当前频道发送一条昨日用户数量变动信息\n- 同时将更新本频道名称为 `📈：昨日变动 变动人数`\n"
                )

        await file_save("./log/yesterday.json", LAdict)  # 保存文件
        print(
            f"[{GetTime()}] [adld] G:{guild_id} C:{channel_id} add by Au:{msg.author_id}"
        )
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] /adld - {result}"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"{err_str}\n\n您可能需要重新设置本频道的追踪器"))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 手动查看服务器的昨日新增
@bot.command(name='ldck', case_sensitive=False)
async def yday_inc_check(msg: Message):
    logging(msg)
    try:
        global LAdict
        if msg.ctx.guild.id in LAdict:
            if LAdict[msg.ctx.guild.id]['date'] != GetDate():  #日期不相等
                await msg.reply(
                    f"昨日用户变动为：{LAdict[msg.ctx.guild.id]['increase']}")
            elif LAdict[msg.ctx.guild.id]['date'] == GetDate():  #日期相等
                await msg.reply(f"设下追踪器还没到一天呢，明天再来试试吧！")
        else:
            await msg.reply(f"您尚未开启本服务器的新增用户追终器，请使用`/adld`开启")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] /ldck - {result}"
        print(err_str)
        await msg.reply(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 关闭服务器的昨日新增追踪器
@bot.command(name='tdld', case_sensitive=False)
async def td_yday_inc_check(msg: Message):
    logging(msg)
    global LAdict
    if msg.ctx.guild.id in LAdict:
        del LAdict[msg.ctx.guild.id]
        await msg.reply(f"已成功取消本服务器的`昨日新增用户`追踪器")
        #最后重新执行写入
        await file_save("./log/yesterday.json", LAdict)
        print(f"[{GetTime()}] Del Yday_Inc: G:{msg.ctx.guild.id}")
    else:
        await msg.reply(f"本服务器暂未开启`昨日新增用户`追踪器")


# 函数供调用
async def yesterday_UIC():
    global LAdict
    LAdict_temp = copy.deepcopy(LAdict)
    for g, s in LAdict_temp.items():
        print(f"[{GetTime()}] Yday_INC %s" % s)  #打印log信息
        try:  # 获取服务器信息
            ret = await server_status(g)
            # 用户不在服务器内（bot被踢了）删除键值
            if ('该用户不在该服务器内' in ret['message']) or ret['code'] != 0:
                log_str = f"ERR! [Yday_INC] {ret}\n"
                log_str += f"[Yday_INC] del G:{g}"
                del LAdict[g]  # 删除服务器
                print(log_str)
                continue

            total = ret['data']['user_count']  # 当前服务器用户数量
            dif = total - s['user_total']  # 文件中存着的用户数量 - 当前
            LAdict[g]['user_total'] = total  # 更新文件中用户数量
            # 更新人数增加数量
            inc_diff = dif - s['increase']
            LAdict[g]['increase'] = dif
            # 选项卡不为0，则执行发送
            if s['option'] != 0:
                ch = await bot.client.fetch_public_channel(s['channel'])
                name_str = "📈：昨日变动 none"
                send_text = "昨日新增用户 ERR"
                if dif > 0:
                    name_str = f"📈：昨日变动 {dif}↑"
                    if inc_diff > 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({inc_diff}↑)\n"
                    elif inc_diff < 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({inc_diff}↓)\n"
                    else:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({inc_diff}-)\n"
                elif dif < 0:
                    name_str = f"📈：昨日变动 {dif}↓"
                    if inc_diff > 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({inc_diff}↑)\n"
                    elif inc_diff < 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({inc_diff}↓)\n"
                    else:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({inc_diff}-)\n"
                else:
                    name_str = f"📈：昨日变动 {dif}-"
                    if inc_diff > 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- ({inc_diff}↑)\n"
                    elif inc_diff < 0:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- ({inc_diff}↓)\n"
                    else:
                        send_text = f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- ({inc_diff}-)\n"

                # 发送/更新频道名字
                await bot.client.send(ch, send_text)
                if s['option'] == 2:
                    await channel_update(s['channel'], name_str)
        except Exception as result:
            err_str = f"ERR! [{GetTime()}] Yday_INC s:{g}\n```\n{traceback.format_exc()}\n```\n"
            print(err_str)
            if "guild_id不存在" in err_str or "没有权限" in err_str:
                del LAdict[g]  # 删除服务器
                print(f"[{GetTime()}] Yday_INC del LAdict[{g}]")
            #发送错误信息到指定频道
            await bot.client.send(debug_ch, err_str)

    #需要重新执行写入（更新）
    await file_save("./log/yesterday.json", LAdict)
    print(f"[BOT.TASK] Yday_INC finished at {GetTime()}")


#定时任务，在0点01分的时候向指定频道发送昨日新增用户数量的提示
@bot.task.add_cron(hour=0, minute=1, timezone="Asia/Shanghai")
async def yesterday_UserIncrease():
    log_flush()
    try:
        await yesterday_UIC()
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] Yday_INC\n```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


@bot.command(name='ync', case_sensitive=False)
async def yesterday_cmd(msg: Message, *arg):
    logging(msg)
    try:
        if msg.author_id == config['master_id']:
            await yesterday_UIC()
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] Yday_INC\n```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        #发送错误信息到指定频道
        await msg.reply(err_str)
        await bot.client.send(debug_ch, err_str)


#######################################服务器在线人数更新###################################################


# 直接查看本服务器状态
@bot.command(name='svck', case_sensitive=False)
async def server_user_check(msg: Message):
    logging(msg)
    try:
        ret = await server_status(msg.ctx.guild.id)
        total = ret['data']['user_count']
        online = ret['data']['online_count']
        await msg.reply(f"当前服务器用户状态为：{online}/{total}")
    except Exception as result:
        err_str = f"ERR! [{GetTime()}] check_server_user_status: ```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        await msg.reply(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 处理转义字符
def fb_modfiy(front: str, back: str):
    front = front.replace('\\', '')
    back = back.replace('\\', '')

    return {'fr': front, 'ba': back}


# 设置在线人数监看
async def Add_server_user_update(msg: Message, ch: str, front: str, back: str):
    try:
        global SVdict
        #用两个flag来分别判断服务器和需要更新的频道是否相同
        flag_gu = 1  #旧服务器
        flag_ch = 1
        if msg.ctx.guild.id not in SVdict:
            flag_gu = 0  #新增服务器
            SVdict[msg.ctx.guild.id] = {'channel': '', 'front': '', 'back': ''}
        if ch != SVdict[msg.ctx.guild.id]['channel']:
            flag_ch = 0  #频道更改
            SVdict[msg.ctx.guild.id]['channel'] = ch

        SVdict[msg.ctx.guild.id]['front'] = front
        SVdict[msg.ctx.guild.id]['back'] = back

        #处理转义字符
        mstr = fb_modfiy(SVdict[msg.ctx.guild.id]['front'],
                         SVdict[msg.ctx.guild.id]['back'])
        SVdict[msg.ctx.guild.id]['front'] = mstr['fr']
        SVdict[msg.ctx.guild.id]['back'] = mstr['ba']

        # 修改了之后立马更新，让用户看到修改后的结果
        ret = await server_status(msg.ctx.guild.id)
        total = ret['data']['user_count']
        online = ret['data']['online_count']
        url = kook_base_url + "/api/v3/channel/update"
        params = {
            "channel_id":
            SVdict[msg.ctx.guild.id]['channel'],
            "name":
            f"{SVdict[msg.ctx.guild.id]['front']}{online}/{total}{SVdict[msg.ctx.guild.id]['back']}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params,
                                    headers=kook_headers) as response:
                ret1 = json.loads(await response.text())

        # 执行不同的提示信息
        if flag_gu == 1 and flag_ch == 1:
            await msg.reply(f"服务器在线人数监看格式已更新！\n前缀 [{front}]\n后缀 [{back}]")
        elif flag_gu == 1 and flag_ch == 0:
            await msg.reply(f"本服务器在线人数监看已修改频道为{ch}\n前缀 [{front}]\n后缀 [{back}]")
        else:
            # ↓服务器id错误时不会执行下面的↓
            print(
                f"First_Update successful! {SVdict[msg.ctx.guild.id]['front']}{online}/{total}{SVdict[msg.ctx.guild.id]['back']}"
            )
            await msg.reply(f'服务器监看系统已添加，首次更新成功！\n前缀 [{front}]\n后缀 [{back}]')

        #不管是否已存在，都需要重新执行写入（更新/添加）
        with open("./log/server.json", 'w', encoding='utf-8') as fw1:
            json.dump(SVdict,
                      fw1,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
        fw1.close()

    except Exception as result:
        err_str = f"[adsv] Au:{msg.author_id}\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"{err_str}\n\n您可能需要重新设置本频道的监看事件"))
        c.append(Module.Divider())
        c.append(
            Module.Section(
                '有任何问题，请加入帮助服务器与我联系',
                Element.Button('帮助', 'https://kook.top/gpbTwZ',
                               Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)


# 手动指定频道id（适用于分组的情况）
@bot.command(name='adsv1', aliases=['在线人数监看1'], case_sensitive=False)
async def adsv_1(msg: Message, front: str = "频道在线 ", back: str = " "):
    logging(msg)
    # 直接执行下面的函数
    ch = msg.ctx.channel.id
    await Add_server_user_update(msg, ch, front, back)


# 手动指定频道id（适用于分组的情况）
@bot.command(name='adsv2', aliases=['在线人数监看2'], case_sensitive=False)
async def adsv_2(msg: Message,
                 ch: str = 'err',
                 front: str = "频道在线 ",
                 back: str = " "):
    logging(msg)
    if ch != 'err':  # 检查频道id是否有效
        url_ch = kook_base_url + "/api/v3/channel/view"
        params = {"target_id": ch}
        async with aiohttp.ClientSession() as session:
            async with session.get(url_ch, data=params,
                                   headers=kook_headers) as response:
                ret = json.loads(await response.text())
        if ret['code'] != 0:  #代表频道是不正确的
            await msg.reply(
                f"频道id参数不正确：`{ret['message']}`\n请确认您输入的是`开发者模式`下复制的`频道id`，而不是频道的名字/服务器id！有任何问题，请点击[按钮](https://kook.top/gpbTwZ)加入帮助频道咨询"
            )
            return
    else:
        await msg.reply(
            f"您使用了`/adsv2`命令，该命令必须指定频道id\n若想在当前频道更新在线人数，请使用`/adsv1`命令\n当然，你手动指定当前频道也不是不行"
        )
        return

    #过了上面的内容之后，执行下面的函数
    await Add_server_user_update(msg, ch, front, back)


# 取消在线人数监看
@bot.command(name='tdsv', aliases=['退订在线人数监看'], case_sensitive=False)
async def Cancel_server_user_update(msg: Message):
    logging(msg)
    global SVdict
    if msg.ctx.guild.id in SVdict:
        await msg.reply(f"已成功取消本服务器的在线人数监看")
        # 保存到文件
        del SVdict[msg.ctx.guild.id]
        with open("./log/server.json", 'w', encoding='utf-8') as fw1:
            json.dump(SVdict,
                      fw1,
                      indent=2,
                      sort_keys=True,
                      ensure_ascii=False)
        print(f"tdsv - Cancel: G:{msg.ctx.guild.id}")
    else:  # 不存在
        await msg.reply(f"本服务器暂未开启在线人数监看")


# 定时更新服务器的在线用户/总用户状态
@bot.task.add_interval(minutes=20)
async def server_user_update():
    global SVdict
    try:
        print(f"[BOT.TASK] server_user_update start at {GetTime()}")
        SVdict_temp = copy.deepcopy(SVdict)  #深拷贝
        log_text = "[BOT.TASK] server_user_update: "
        for g, s in SVdict_temp.items():
            try:
                log_text += f"({g}) "
                # 调用api进行更新
                ret = await server_status(g)
                if ('该用户不在该服务器内' in ret['message']) or ret['code'] != 0:
                    log_str = f"ERR! [GusrUPD] {ret}\n"
                    log_str += f"[GusrUPD] Del G:{g} D:{s}"
                    del SVdict[g]  #删除键值
                    print(log_str)
                    continue

                total = ret['data']['user_count']
                online = ret['data']['online_count']
                url = kook_base_url + "/api/v3/channel/update"
                params = {
                    "channel_id": s['channel'],
                    "name": f"{s['front']}{online}/{total}{s['back']}"
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url,
                                            data=params,
                                            headers=kook_headers) as response:
                        ret1 = json.loads(await response.text())
            except Exception as result:
                err_cur = str(traceback.format_exc())
                err_str = f"ERR! [{GetTime()}] update_server_user_status:{g}\n```\n{err_cur}\n```\n"
                print(err_str)
                if "json.decoder.JSONDecodeError" in err_cur:
                    print(await response.text())
                elif "guild_id不存在" in err_str or "没有权限" in err_str:
                    del SVdict[g]  # 删除服务器
                    print(
                        f"[{GetTime()}] server_user_update | del SVdict[{g}]")
                elif 'connect to' in err_str:  # 网络问题
                    print(f"[{GetTime()}] server_user_update | {err_str}")
                # 发送错误信息到指定频道
                await bot.client.send(debug_ch, err_str)

        # 不相同代表有删除，保存
        if SVdict_temp != SVdict:
            await file_save("./log/server.json", SVdict)
        # 打印log过程
        print(log_text)
    except Exception as result:
        if 'connect to' in str(result):  # 网络问题
            return print(
                f"[{GetTime()}] server_user_update_status | {str(result)}")
        # 打印错误
        err_str = f"ERR! [{GetTime()}] update_server_user_status:\n```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch, err_str)


# 开机任务
@bot.task.add_date()
async def startup_task():
    try:
        global debug_ch
        debug_ch = await bot.client.fetch_public_channel(config['debug_ch'])
        print(f"[Start] fetch debug channel success")
        log_flush()
    except:
        err_cur = str(traceback.format_exc())
        print(f"ERR ON START UP!\n{err_cur}")
        log_flush()
        os._exit(-1)

# 开机
if __name__ == '__main__':
    # 开机的时候打印一次时间，记录重启时间
    print(f"[Start] at [%s]" % GetTime())
    # 开机
    bot.run()