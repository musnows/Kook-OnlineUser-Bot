# encoding: utf-8:
import os
import json
import time
import copy
import aiohttp
import traceback

from khl import Bot, Message, EventTypes
from khl.card import CardMessage, Card, Module, Element, Types


# 配置机器人
with open('./config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
# 用读取来的 config 初始化 bot，字段对应即可
bot = Bot(token=config['token'])

Botoken=config['token']
kook="https://www.kookapp.cn"
headers={f'Authorization': f"Bot {Botoken}"}
debug_ch=None

# 向botmarket通信
@bot.task.add_interval(minutes=30)
async def botmarket():
    api ="http://bot.gekj.net/api/v1/online.bot"
    headers = {'uuid':'8b3b4c14-d20c-4a23-9c71-da4643b50262'}
    async with aiohttp.ClientSession() as session:
        await session.post(api, headers=headers)

#############################################################################################


def GetTime(): #将获取当前时间封装成函数方便使用
    return time.strftime("%y-%m-%d %H:%M:%S", time.localtime())

def GetDate(): #将获取当前日期成函数方便使用
    return time.strftime("%y-%m-%d", time.localtime())

# 在控制台打印msg内容，用作日志
def logging(msg: Message):
    now_time = GetTime()
    print(f"[{now_time}] G:{msg.ctx.guild.id} - C:{msg.ctx.channel.id} - Au:{msg.author_id}_{msg.author.username}#{msg.author.identify_num} = {msg.content}")

# 查看bot状态
@bot.command(name='alive')
async def alive_check(msg:Message,*arg):
    logging(msg)
    await msg.reply(f"bot alive here")

# 帮助命令
@bot.command(name='CKhelp',aliases=['ckhelp,chelp,khelp'])
async def help(msg:Message):
    logging(msg)
    cm = CardMessage()
    c3 = Card(Module.Header('目前在线/总人数小助手支持的指令如下'),Module.Context(Element.Text("由MOAR#7134开发，开源代码见 [Github](https://github.com/Aewait/Kook-OnlineUser-Bot)",Types.Text.KMD)))
    c3.append(Module.Divider())
    #实现卡片的markdown文本
    c3.append(Module.Header('服务器在线/总人数监看'))
    help_Str1 ="`/alive` 看看bot是否在线\n"
    help_Str1+="`/svck` 查看当前服务器的在线/总人数\n"
    help_Str1+="`/adsv1 '前缀' '后缀'` 在当前频道设置本服务器的在线人数更新\n"
    help_Str1+="`/adsv2 频道id '前缀' '后缀' ` 在指定频道设置本服务器的在线人数更新\n"
    c3.append(Module.Section(Element.Text(help_Str1,Types.Text.KMD)))
    c3.append(Module.Section(Element.Text("```\n频道/分组id获取：打开`设置-高级-开发者模式`，右键频道复制id\n```",Types.Text.KMD)))
    help_Str2 ="注意`频道id`参数不是`频道名字`！上方有提示\n默认格式为`频道在线 10/100`。其中`频道在线 `为前缀，默认后缀为`空`。可以手动指定前缀和后缀，来适应你的频道的命名风格。记得加**英文的引号**来保证前缀/后缀的完整性！示例:\n```\n/adsv 0000000 \"频道在线 | \" \" 测试ing\"\n```\n"
    help_Str2+="在线人数监看设定为30分钟更新一次\n"
    help_Str2+="`/tdsv` 取消本服务器的在线人数监看\n"
    c3.append(Module.Section(Element.Text(help_Str2,Types.Text.KMD)))
    c3.append(Module.Divider())
    c3.append(Module.Header('服务器昨日新增用户追踪'))
    help_Str3 ="`/adld` 在当前服务器开启`昨日新增用户`追踪器；\n"
    help_Str3+="`/adld 1`会设置定时任务，每日00:00向`当前频道`发送昨日新增用户的数量\n"
    help_Str3+="`/adld 2`则会向当前频道发送消息的同时，更新频道名字\n"
    help_Str3+="`/ldck` 手动查看本服务器的昨日新增用户数量\n"
    help_Str3+="`/tdld` 关闭本服务器的`昨日新增用户`追踪器\n"
    c3.append(Module.Section(Element.Text(help_Str3,Types.Text.KMD)))
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

# 将文件作为全局变量打开（预加载）
with open("./log/yesterday.json",'r',encoding='utf-8') as frla:
    LAlist = json.load(frla)

#设置监看并在指定频道发送信息
@bot.command(name='adld')
async def Add_YUI_ck(msg:Message,op:int=0):
    logging(msg)
    if op <0 or op >2:
        await msg.reply(f"选项参数错误，目前只支持 \n0:不推送信息\n1:在本频道推送信息\n2:推送信息的同时修改本频道名")
        return 

    try:
        global LAlist
        LastDay['guild']=msg.ctx.guild.id
        LastDay['channel']=msg.ctx.channel.id
        LastDay['option']=op # 1为启用发送,0为不启用
        LastDay['date']= GetDate()
        
        flag_op=0
        flag_sv=0
        # with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
        #     LAlist = json.load(fr1)
        
        for s in LAlist:
            if s['guild'] == LastDay['guild']:
                flag_sv=1
                s['channel']=LastDay['channel']
                if s['option'] != op:
                    flag_op=1
                    s['option']=op#更新选项
                break
        #print(flag_sv,' ',flag_op)
        if flag_sv==1 and flag_op==1 and op==1:
            await msg.reply(f"已在本频道开启`昨日新增用户`的提醒信息推送！")
        elif flag_sv==1 and flag_op==1 and op==2:
            await msg.reply(f"已在本频道开启`昨日新增用户`的提醒信息推送！bot同时会更新本频道名称为 `📈：昨日变动 变动人数`\n")
        elif flag_sv==1 and flag_op==1 and op==0:
            await msg.reply(f"已关闭本频道的`昨日新增用户`的提醒信息推送！\n- 追踪仍在进行，您可以用`/ldck`功能手动查看昨日新增\n或用`/tdld`功能关闭本服务器的新增用户追踪器")
        elif flag_sv==1 and flag_op==0:
            await msg.reply(f"本服务器`昨日新增用户`追踪器已开启，请勿重复操作")
        elif flag_sv==0:
            # 获取当前服务器总人数，作为下次更新依据
            ret = await server_status(LastDay['guild']) #print(ret)
            LastDay['user_total']=ret['data']['user_count']
            LastDay['increase']=0
            LAlist.append(LastDay)
            if op == 0:
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启！\n- 您没有设置第二个参数，bot不会自动发送推送信息。可在明日用`/ldck`手动查看昨日新增，或重新操作本指令\n- 若需要在本频道开启信息推送，需要添加第二个非零数字作为参数：`/adld 1`")
            elif op == 1:
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启！\n- 您设置了第二个参数`1`，bot会在每天的00:00向当前频道发送昨日用户数量变动信息\n")
            elif op == 2: 
                await msg.reply(f"本服务器`昨日新增用户`追踪器已开启！\n- 您设置了第二个参数`2`，bot会在每天的00:00向当前频道发送一条昨日用户数量变动信息\n- 同时将更新本频道名称为 `📈：昨日变动 变动人数`\n")

        with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
                json.dump(LAlist,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        err_str=f"ERR! [{GetTime()}] /adld - {result}"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"{err_str}\n\n您可能需要重新设置本频道的追踪器"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch,err_str)


# 手动查看服务器的昨日新增
@bot.command(name='ldck')
async def yday_inc_check(msg:Message):
    logging(msg)

    # with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
    #     LAlist = json.load(fr1)
    global LAlist
    for s in LAlist:
        if s['guild'] == msg.ctx.guild.id and s['date']!=GetDate():
            await msg.reply(f"昨日用户变动为：{s['increase']}")
            return
        elif s['guild'] == msg.ctx.guild.id and s['date']==GetDate():
            await msg.reply(f"设下追踪器还没到一天呢，明天再来试试吧！")
            return
    
    await msg.reply(f"您尚未开启本服务器的新增用户追终器，请使用`/adld`开启")


# 关闭服务器的昨日新增追踪器
@bot.command(name='tdld')
async def td_yday_inc_check(msg:Message):
    logging(msg)
    global LAlist
    emptyList = list() #空list
    # with open("./log/yesterday.json",'r',encoding='utf-8') as fr1:
    #     data = json.load(fr1)
    flag = 0 #用于判断
    for s in LAlist:
        if s['guild']==msg.ctx.guild.id:
            flag = 1
            print(f"Cancel Yday_Inc: G:{s['guild']} - C:{s['channel']}")
            await msg.reply(f"已成功取消本服务器的`昨日新增用户`追踪器")
        else: # 不吻合，进行插入
            emptyList.append(s)

    #最后重新执行写入
    LAlist=emptyList
    with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
        json.dump(LAlist,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
    fw1.close()

    if flag == 0:
        await msg.reply(f"本服务器暂未开启`昨日新增用户`追踪器")


#定时任务，在0点01分的时候向指定频道发送昨日新增用户数量的提示
@bot.task.add_cron(hour=0,minute=1,timezone="Asia/Shanghai")
async def yesterday_UserIncrease():
    global LastDay,LAlist
    try:
        LAlist_temp = copy.deepcopy(LAlist)
        for s in LAlist_temp:
            now_time=GetTime()
            print(f"[{now_time}] Yday_INC %s"%s)#打印log信息
            try:
                ret = await server_status(s['guild'])
                if ('该用户不在该服务器内' in ret['message']) or ret['code']!=0:
                    log_str = f"ERR! [Yday_INC] {ret}\n"
                    log_str +=f"[Yday_INC] del {s}"
                    LAlist.remove(s)
                    print(log_str)
                    continue
                    
                total=ret['data']['user_count']
                dif= total - s['user_total']
                s['user_total']=total
                # 选项卡不为0，则执行发送
                ch=await bot.client.fetch_public_channel(s['channel'])
                if s['option'] == 1 and dif>s['increase']:
                    if dif>0:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ (+{dif-s['increase']}↑)\n")
                    else:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ (+{dif-s['increase']}↑)\n")
                elif s['option'] == 1 and dif<s['increase']:
                    if dif>0:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({dif-s['increase']}↓)\n")
                    else:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({dif-s['increase']}↓)\n")
                elif s['option'] == 1 and dif==s['increase']:
                    if dif>0:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({dif-s['increase']}-)\n")
                    else:
                        await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({dif-s['increase']}-)\n")
                elif s['option'] == 2:
                    url=kook+"/api/v3/channel/update"
                    params={}
                    if dif>0:
                        params = {"channel_id":s['channel'],"name":f"📈：昨日变动 {dif}↑"}
                        if dif>s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ (+{dif-s['increase']}↑)\n")
                        elif dif<s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({dif-s['increase']}↓)\n")
                        else:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↑ ({dif-s['increase']}-)\n")
                    elif dif<0:
                        params = {"channel_id":s['channel'],"name":f"📈：昨日变动 {dif}↓"}
                        if dif>s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ (+{dif-s['increase']}↑)\n")
                        elif dif<s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({dif-s['increase']}↓)\n")
                        else:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`↓ ({dif-s['increase']}-)\n")
                    elif dif==0:
                        params = {"channel_id":s['channel'],"name":f"📈：昨日变动 {dif}-"}
                        if dif>s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- (+{dif-s['increase']}↑)\n")
                        elif dif<s['increase']:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- ({dif-s['increase']}↓)\n")
                        else:
                            await bot.client.send(ch,f"新的一天开始啦！本服务器昨日用户变动: `{dif}`- ({dif-s['increase']}-)\n")

                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, data=params,headers=headers) as response:
                            ret1= json.loads(await response.text())
                            print(f"Option=2, Update_ch: {ret1['message']}")

                s['increase']=dif
            except Exception as result:
                err_str=f"ERR! [{GetTime()}] Yday_INC s:{s['guild']} - ```\n{traceback.format_exc()}\n```\n"
                print(err_str)
                #发送错误信息到指定频道
                await bot.client.send(debug_ch,err_str)

        #需要重新执行写入（更新）
        with open("./log/yesterday.json",'w',encoding='utf-8') as fw1:
            json.dump(LAlist,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()
        print("[BOT.TASK] Yday_INC finished!")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] Yday_INC - ```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch,err_str)
    

#######################################服务器在线人数更新###################################################

# 预加载
with open("./log/server.json",'r',encoding='utf-8') as frsv:
    SVdict = json.load(frsv)

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
        err_str=f"ERR! [{GetTime()}] check_server_user_status: ```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        await msg.reply(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch,err_str)

# 处理转义字符
def fb_modfiy(front:str,back:str):
    # front=front.replace('\-','-')
    # back=back.replace('\-','-')

    # front=front.replace('\\\\','\\')
    # back=back.replace('\\\\','\\')
    # print(f"{front}  {back}")
    front=front.replace('\\','')
    back=back.replace('\\','')

    return {'fr':front,'ba':back}


# 设置在线人数监看
async def Add_server_user_update(msg:Message,ch:str,front:str,back:str):
    try:
        global  SVdict
        #用两个flag来分别判断服务器和需要更新的频道是否相同
        flag_gu = 1 #旧服务器
        flag_ch = 1    
        if msg.ctx.guild.id not in SVdict:
            flag_gu = 0 #新增服务器
            SVdict[msg.ctx.guild.id] = {'channel':'','front':'','back':''}
        if ch != SVdict[msg.ctx.guild.id]['channel']:
            flag_ch = 0 #频道更改
            SVdict[msg.ctx.guild.id]['channel']=ch

        SVdict[msg.ctx.guild.id]['front']=front
        SVdict[msg.ctx.guild.id]['back']=back

    
        #处理转义字符
        mstr = fb_modfiy(SVdict[msg.ctx.guild.id]['front'],SVdict[msg.ctx.guild.id]['back'])
        SVdict[msg.ctx.guild.id]['front']=mstr['fr']
        SVdict[msg.ctx.guild.id]['back']=mstr['ba']

        # 修改了之后立马更新，让用户看到修改后的结果
        ret = await server_status(msg.ctx.guild.id)
        total=ret['data']['user_count']
        online=ret['data']['online_count']
        url=kook+"/api/v3/channel/update"
        params = {"channel_id":SVdict[msg.ctx.guild.id]['channel'],"name":f"{SVdict[msg.ctx.guild.id]['front']}{online}/{total}{SVdict[msg.ctx.guild.id]['back']}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params,headers=headers) as response:
                ret1= json.loads(await response.text())
        
        # 执行不同的提示信息
        if flag_gu == 1 and flag_ch==1:
            await msg.reply(f"服务器在线人数监看格式已更新！\n前缀 [{front}]\n后缀 [{back}]")
        elif flag_gu ==1 and flag_ch == 0:
            await msg.reply(f"本服务器在线人数监看已修改频道为{ch}\n前缀 [{front}]\n后缀 [{back}]")
        else:            
            # ↓服务器id错误时不会执行下面的↓
            print(f"First_Update successful! {SVdict[msg.ctx.guild.id]['front']}{online}/{total}{SVdict[msg.ctx.guild.id]['back']}")
            await msg.reply(f'服务器监看系统已添加，首次更新成功！\n前缀 [{front}]\n后缀 [{back}]')

        #不管是否已存在，都需要重新执行写入（更新/添加）
        with open("./log/server.json",'w',encoding='utf-8') as fw1:
            json.dump(SVdict,fw1,indent=2,sort_keys=True, ensure_ascii=False)        
        fw1.close()

    except Exception as result:
        err_str=f"[adsv] Au:{msg.author_id}\n```\n{traceback.format_exc()}\n```"
        print(err_str)
        cm2 = CardMessage()
        c = Card(Module.Header(f"很抱歉，发生了一些错误"))
        c.append(Module.Divider())
        c.append(Module.Section(f"{err_str}\n\n您可能需要重新设置本频道的监看事件"))
        c.append(Module.Divider())
        c.append(Module.Section('有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
        cm2.append(c)
        await msg.reply(cm2)

# 手动指定频道id（适用于分组的情况）
@bot.command(name='adsv1',aliases=['在线人数监看2'])
async def adsv_1(msg:Message,front:str="频道在线 ",back:str=" "):
    logging(msg)
    # 直接执行下面的函数
    ch=msg.ctx.channel.id
    await Add_server_user_update(msg,ch,front,back)


# 手动指定频道id（适用于分组的情况）
@bot.command(name='adsv2',aliases=['在线人数监看2'])
async def adsv_2(msg:Message,ch:str='err',front:str="频道在线 ",back:str=" "):
    logging(msg)
    if ch != 'err':# 检查频道id是否有效
        url_ch = kook+"/api/v3/channel/view"
        params = {"target_id":ch}
        async with aiohttp.ClientSession() as session:
            async with session.get(url_ch, data=params,headers=headers) as response:
                ret= json.loads(await response.text())
        if ret['code']!=0: #代表频道是不正确的
            await msg.reply(f"频道id参数不正确：`{ret['message']}`\n请确认您输入的是`开发者模式`下复制的`频道id`，而不是频道的名字/服务器id！有任何问题，请点击[按钮](https://kook.top/gpbTwZ)加入帮助频道咨询")
            return
    else:
        await msg.reply(f"您使用了`/adsv2`命令，该命令必须指定频道id\n若想在当前频道更新在线人数，请使用`/adsv1`命令\n当然，你手动指定当前频道也不是不行")
        return
    
    #过了上面的内容之后，执行下面的函数
    await Add_server_user_update(msg,ch,front,back)




# 取消在线人数监看
@bot.command(name='tdsv',aliases=['退订在线人数监看'])
async def Cancel_server_user_update(msg:Message):
    logging(msg)
    global SVdict
    if msg.ctx.guild.id in SVdict:
        await msg.reply(f"已成功取消本服务器的在线人数监看")
        # 保存到文件
        del SVdict[msg.ctx.guild.id]
        with open("./log/server.json",'w',encoding='utf-8') as fw1:
            json.dump(SVdict,fw1,indent=2,sort_keys=True, ensure_ascii=False)
        print(f"tdsv - Cancel: G:{msg.ctx.guild.id}")
    else: # 不存在
        await msg.reply(f"本服务器暂未开启在线人数监看")
    

# 定时更新服务器的在线用户/总用户状态
@bot.task.add_interval(minutes=20)
async def server_user_update():
    global SVdict
    try:
        print("[BOT.TASK] server_user_update start")
        SVdict_temp = copy.deepcopy(SVdict)#深拷贝
        for g,s in SVdict_temp.items():
            try:
                now_time=GetTime()
                print(f"[{now_time}] Upd G:{g}")#打印log信息
                # 调用api进行更新
                ret = await server_status(g)
                if ('该用户不在该服务器内' in ret['message']) or ret['code']!=0:
                    log_str = f"ERR! [GusrUPD] {ret}\n"
                    log_str +=f"[GusrUPD] Del G:{g} D:{s}"
                    del SVdict[g] #删除键值
                    print(log_str)
                    continue
                
                total=ret['data']['user_count']
                online=ret['data']['online_count']
                url=kook+"/api/v3/channel/update"
                params = {"channel_id":s['channel'],"name":f"{s['front']}{online}/{total}{s['back']}"}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=params,headers=headers) as response:
                            ret1= json.loads(await response.text())
            except Exception as result:
                err_cur=str(traceback.format_exc()) 
                err_str=f"ERR! [{GetTime()}] update_server_user_status:{g}\n```\n{err_cur}\n```\n"             
                print(err_str)
                if "json.decoder.JSONDecodeError" in err_cur:
                    print(await response.text())
                #发送错误信息到指定频道
                await bot.client.send(debug_ch,err_str)

        # 不相同代表有删除，保存
        if SVdict_temp != SVdict:
            with open("./log/server.json",'w',encoding='utf-8') as fw1:
                json.dump(SVdict,fw1,indent=2,sort_keys=True, ensure_ascii=False)
                
        print("[BOT.TASK] server_user_update finished")
    except Exception as result:
        err_str=f"ERR! [{GetTime()}] update_server_user_status: ```\n{traceback.format_exc()}\n```\n"
        print(err_str)
        #发送错误信息到指定频道
        await bot.client.send(debug_ch,err_str)

# 开机任务
@bot.task.add_date()
async def startup_task():
    try:
        global debug_ch
        debug_ch = await bot.client.fetch_public_channel(config['debug_ch'])
        print(f"[Start] fetch debug channel success")
    except:
        err_cur=str(traceback.format_exc())
        print(f"ERR ON START UP!\n{err_cur}")
        os._exit(-1)

# 开机的时候打印一次时间，记录重启时间
print(f"[Start] at [%s]"%GetTime())
# 开机
bot.run()