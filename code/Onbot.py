# encoding: utf-8:
import json
from sched import scheduler
import time
import aiohttp
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from khl import Bot, Message, EventTypes
from khl.card import CardMessage, Card, Module, Element, Types


from warnings import filterwarnings
from pytz_deprecation_shim import PytzUsageWarning
#忽略相关警告
filterwarnings('ignore', category=PytzUsageWarning)


# 配置机器人
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

Botoken=config['token']
kook="https://www.kookapp.cn"
headers={f'Authorization': f"Bot {Botoken}"}

# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'8b3b4c14-d20c-4a23-9c71-da4643b50262'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)

#############################################################################################

Debug_ch="6248953582412867"

def GetTime(): #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

def GetDate(): #将获取当前日期成函数方便使用
    return time.strftime("%y-%m-%d", time.localtime())

# 开机的时候打印一次时间，记录重启时间
print(f"Start at: [%s]"%GetTime())

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")

# 查看bot状态
@bot.command(name='alive')
async def alive_check(msg:Message):
    logging(msg)
    await msg.reply(f"bot alive here")

# 帮助命令
@bot.command(name='CKhelp')
async def help(msg:Message):
    logging(msg)
    cm = CardMessage()
    c3 = Card(Module.Header('目前在线/总人数小助手支持的指令如下'),Module.Context(Element.Text("由MOAR#7134开发，开源代码见 [Github](https://github.com/Aewait/Kook-OnlineUser-Bot)",Types.Text.KMD)))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    c3.append(Module.Header('服务器在线/总人数监看'))
    help_Str1="`/alive` 看看bot是否在线\n"
    help_Str1+="`/svck` 查看当前服务器的在线/总人数\n"
    help_Str1+="`/adck 频道id '前缀' '后缀'` 设置在本服务器的在线人数更新\n默认格式为`频道在线 10/100`。其中`频道在线 `为前缀，默认后缀为空。可以手动指定前缀和后缀，来适应你的频道的命名风格。记得加**英文的引号**来保证前缀/后缀的完整性！\n```\n/adck 111111111 '频道在线 | ' ' 测试ing'\n```\n"
    help_Str1+="在线人数监看设定为30分钟更新一次\n"
    help_Str1+="`/tdck` 取消本服务器的在线人数监看\n"
    c3.append(Module.Section(Element.Text(help_Str1,Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section(Element.Text("频道/分组id获取：打开`设置-高级-开发者模式`，右键频道复制id",Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header('服务器昨日新增用户追踪'))
    help_Str2="`/adld` 在当前服务器开启`昨日新增用户`追踪器；添加第二个参数`/adld 1`则会设置定时任务，每日00:00向`当前频道`发送昨日新增用户的数量\n"
    help_Str2+="`/ldck` 手动查看本服务器的昨日新增用户数量\n"
    help_Str2+="`/tdld` 关闭本服务器的`昨日新增用户`追踪器\n"
    c3.append(Module.Section(Element.Text(help_Str2,Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
              Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c3)
    await msg.reply(cm)



# 获取服务器用户数量用于更新
async def server_status(Gulid_ID:str):
    url=kook+"/api/v3/guild/user-list"
    params = {"guild_id":Gulid_ID}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params,headers=headers) as response:
                ret1= json.loads(await response.text())
                #print(ret1)
                return ret1


#######################################服务器昨日新增用户数量###############################################

LastDay={
    'guild':'',
    'channel':'',
    'user_total':'',
    'increase':'',
    'date':'',
    'option':0
}

#设置监看并在指定频道发送信息
@bot.command(name='adld')
async def Add_YUI_ck(msg:Message,op:int=0):
    logging(msg)
    try:
        global LastDay
        LastDay['guild']=msg.ctx.guild.id
        LastDay['channel']=msg.ctx.channel.id
        LastDay['option']=op # 1为启用发送,0为不启用
        LastDay['date']= GetDate()
        
        flag_op=0
        flag_sv=0
        with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
            LAlist = json.load(fr1)
        
        for s in LAlist:
            if s['guild'] == LastDay['guild']:
                flag_sv=1
                s['channel']=LastDay['channel']
                if s['option'] != op:
                    flag_op=1
                    s['option']=op#更新选项
                
                break
                
        if flag_sv==1 and flag_op==1 and op!=0:
            await msg.reply(f"已在本频道开启`昨日新增用户`的提醒信息推送！")
        elif flag_sv==1 and flag_op==1 and op==0:
            await msg.reply(f"已关闭本频道的`昨日新增用户`的提醒信息推送！\n- 追踪仍在进行，您可以用`/ldck`功能手动查看昨日新增\n或用`/tdld`功能关闭本服务器的新增用户追踪器")
        elif flag_sv==1 and flag_op==0:
            await msg.reply(f"本服务器`昨日新增用户`追踪器已开启，请勿重复操作")
        elif flag_sv==0:
            # 获取当前服务器总人数，作为下次更新依据
            ret = await server_status(LastDay['guild'])
            LastDay['user_total']=ret['data']['user_count']
            LastDay['increase']=0
            LAlist.append(LastDay)
            if op == 0:
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启！\n- 您没有设置第二个参数，bot不会自动发送推送信息。可在明日用`/ldck`手动查看昨日新增，或重新操作本指令\n- 若需要在本频道开启信息推送，需要添加第二个非零数字作为参数：`/adld 1`")
            else:
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启！\n- 您设置了第二个参数，bot会在每天的00:00向当前频道发送一条昨日用户数量变动信息\n")

        with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
                json.dump(LAlist,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】 {result}\n\n您可能需要重新设置本频道的追踪器"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

        err_str=f"ERR! [{GetTime()}] /adld - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)


# 手动查看服务器的昨日新增
@bot.command(name='ldck')
async def yday_inc_check(msg:Message):
    logging(msg)

    with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
        LAlist = json.load(fr1)
    
    for s in LAlist:
        if s['guild'] == msg.ctx.guild.id and s['date']!=GetDate():
            await msg.reply(f"昨日新增用户为：{s['increase']}")
            return
        elif s['guild'] == msg.ctx.guild.id and s['date']==GetDate():
            await msg.reply(f"设下追踪器还没到一天呢，明天再来试试吧！")
            return
    
    await msg.reply(f"您尚未开启本服务器的新增用户追终器，请使用`/adld`开启")


# 关闭服务器的昨日新增追踪器
@bot.command(name='tdld')
async def td_yday_inc_check(msg:Message):
    logging(msg)
    global LastDay
    emptyList = list() #空list
    with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
        data = json.load(fr1)
    flag = 0 #用于判断
    for s in data:
        if s['guild']==msg.ctx.guild.id:
            flag = 1
            print(f"Cancel: G:{s['guild']} - C:{s['channel']}")
            await msg.reply(f"已成功取消本服务器的`昨日新增用户`追踪器")
        else: # 不吻合，进行插入
            #先自己创建一个元素
            LastDay['guild']=s['guild']
            LastDay['channel']=s['channel']
            LastDay['user_total']=s['user_total']
            LastDay['increase']=s['increase']
            LastDay['date']=s['date']
            LastDay['option']=s['option']
            #插入进空list
            emptyList.append(LastDay)

    #最后重新执行写入
    with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
        json.dump(emptyList,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
    fw1.close()

    if flag == 0:
        await msg.reply(f"本服务器暂未开启`昨日新增用户`追踪器")


# 昨日新增用户记录（自动更新）
async def yesterday_UserIncrease():
    try:
        with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
            LAlist = json.load(fr1)

        for s in LAlist:
            now_time=GetTime()
            print(f"[{now_time}] Yday_INC %s"%s)#打印log信息

            ret = await server_status(s['guild'])
            total=ret['data']['user_count']
            dif= total - s['user_total']
            s['increase']=dif
            s['user_total']=total
            # 选项卡不为1，则执行发送
            if s['option'] != 1:
                ch=await bot.fetch_public_channel(s['channel'])
                await bot.send(ch,f"新的一天开始啦！本服务器昨日新增用户: {dif}\n")

        #需要重新执行写入（更新）
        with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
            json.dump(LAlist,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        err_str=f"ERR! [{GetTime()}] Yday_INC - {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)
    

#定时任务，在0点01分的时候向指定频道发送昨日新增用户数量的提示
scheduler = AsyncIOScheduler()
scheduler.add_job(yesterday_UserIncrease,'cron',hour=00,minute=1)
scheduler.start()


#######################################服务器在线人数更新###################################################

# 用于记录服务器信息
ServerDict={
    'guild':'',
    'channel':'',
    'front':'',
    'back':''
}

# 直接查看本服务器状态
@bot.command(name='svck')
async def server_user_check(msg:Message):
    logging(msg)
    try:
        ret = await server_status(msg.ctx.guild.id)
        total=ret['data']['user_count']
        online=ret['data']['online_count']
        await msg.reply(f"当前服务器用户状态为：{online}/{total}")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] check_server_user_status: {result}"
        print(err_str)
        await msg.reply(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)


# 设置在线人数监看
@bot.command(name='adck',aliases=['在线人数监看'])
async def Add_server_user_update(msg:Message,ch:str="err",front:str="频道在线 ",back:str=" "):
    logging(msg)
    if ch == 'err':
        await msg.reply(f"您尚未指定用于更新状态的频道！channel: {ch}")
        return

    try:
        global  ServerDict
        ServerDict['guild']=msg.ctx.guild.id
        ServerDict['channel']=ch
        ServerDict['front']=front
        ServerDict['back']=back

        #用两个flag来分别判断服务器和需要更新的频道是否相同
        flag_gu = 0
        flag_ch = 0
        with open("./log/server.json",'r',encoding='utf-8') as fr1:
            data = json.load(fr1)
        for s in data:
            if s['guild'] == msg.ctx.guild.id:
                if s['channel']==ch:
                    flag_ch = 1
                else:
                    s['channel']=ch
                
                s['front']=front
                s['back']=back
                flag_gu = 1
                # 修改了之后立马更新，让用户看到修改后的结果
                ret = await server_status(msg.ctx.guild.id)
                total=ret['data']['user_count']
                online=ret['data']['online_count']
                url=kook+"/api/v3/channel/update"
                params = {"channel_id":ch,"name":f"{s['front']}{online}/{total}{s['back']}"}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=params,headers=headers) as response:
                        ret1= json.loads(await response.text())
                break
        
        # 执行不同的提示信息
        if flag_gu == 1 and flag_ch==1:
            await msg.reply(f"服务器在线人数监看格式已更新！\n前缀 [{front}]\n后缀 [{back}]")
        elif flag_gu ==1 and flag_ch == 0:
            await msg.reply(f"本服务器在线人数监看已修改频道为{ch}\n前缀 [{front}]\n后缀 [{back}]")
        else:
            # 直接执行第一次更新
            ret = await server_status(msg.ctx.guild.id)
            total=ret['data']['user_count']
            online=ret['data']['online_count']
            url=kook+"/api/v3/channel/update"
            params = {"channel_id":ch,"name":f"{ServerDict['front']}{online}/{total}{ServerDict['back']}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params,headers=headers) as response:
                        ret1= json.loads(await response.text())
            
            # ↓服务器id错误时不会执行下面的↓
            await msg.reply(f'服务器监看系统已添加，首次更新成功！\n前缀 [{front}]\n后缀 [{back}]')
            #将ServerDict添加进list
            data.append(ServerDict)
        
        #不管是否已存在，都需要重新执行写入（更新/添加）
        with open("./log/server.json",'w',encoding='utf-8') as fw1:
            json.dump(data,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"【报错】  {result}\n\n您可能需要重新设置本频道的监看事件"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/Lsv21o', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# 取消在线人数监看
@bot.command(name='tdck',aliases=['退订在线人数监看'])
async def Cancel_server_user_update(msg:Message):
    logging(msg)
    global ServerDict
    emptyList = list() #空list
    with open("./log/server.json",'r',encoding='utf-8') as fr1:
        data = json.load(fr1)
    flag = 0 #用于判断
    for s in data:
        if s['guild']==msg.ctx.guild.id:
            flag = 1
            print(f"Cancel: G:{s['guild']} - C:{s['channel']}")
            await msg.reply(f"已成功取消本服务器的在线人数监看")
        else: # 不吻合，进行插入
            #先自己创建一个元素
            ServerDict['guild']=s['guild']
            ServerDict['channel']=s['channel']
            ServerDict['front']=s['front']
            ServerDict['back']=s['back']
            #插入进空list
            emptyList.append(ServerDict)

    #最后重新执行写入
    with open("./log/server.json",'w',encoding='utf-8') as fw1:
        json.dump(emptyList,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
    fw1.close()

    if flag == 0:
        await msg.reply(f"本服务器暂未开启在线人数监看")


# 定时更新服务器的在线用户/总用户状态
@bot.task.add_interval(minutes=30)
async def server_user_update():
    try:
        with open("./log/server.json",'r',encoding='utf-8') as fr1:
            svlist = json.load(fr1)

        for s in svlist:
            now_time=GetTime()
            print(f"[{now_time}] Updating: %s"%s)#打印log信息

            ret = await server_status(s['guild'])
            total=ret['data']['user_count']
            online=ret['data']['online_count']
            url=kook+"/api/v3/channel/update"
            params = {"channel_id":s['channel'],"name":f"{s['front']}{online}/{total}{s['back']}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params,headers=headers) as response:
                        ret1= json.loads(await response.text())
            
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] update_server_user_status: {result}"
        print(err_str)
        #发送错误信息到指定频道
        debug_channel= await bot.fetch_public_channel(Debug_ch)
        await bot.send(debug_channel,err_str)


bot.run()