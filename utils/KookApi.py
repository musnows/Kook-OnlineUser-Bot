import json
import aiohttp
from khl.card import CardMessage,Card,Module,Element,Types
from .file.Files import BotToken

kook_base_url = "https://www.kookapp.cn"
"""kook api基础url"""
kook_headers = {f'Authorization': f"Bot {BotToken}"}
"""kook api基础kook_headers"""


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

# 通过json服务器小工具获取当前在线人数
async def server_alive_count_weidget(guild_id:str):
    url = kook_base_url + f"/api/guilds/{guild_id}/widget.json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=kook_headers) as response:
            ret = {}
            # 如果服务器没有开小工具会返回403，不能加载json
            if response.status == 200:
                ret = json.loads(await response.text())
            return ret

# 更新频道名字
async def channel_update(channel_id: str, name: str):
    url = kook_base_url + "/api/v3/channel/update"
    params = {"channel_id": channel_id, "name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=params,
                                headers=kook_headers) as response:
            ret1 = json.loads(await response.text())
            return ret1


async def channel_view(channel_id:str):
    """获取频道信息，可以用于判断频道id是否正确"""
    url = kook_base_url + "/api/v3/channel/view"
    params = {"target_id": channel_id}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=params,
                                headers=kook_headers) as response:
            ret = json.loads(await response.text())
            return ret


async def get_card(text: str,
                   sub_text='e',
                   img_url='e',
                   card_color='#fb4b57',
                   img_sz='sm') -> Card:
    """获取常用的卡片消息的卡片。有缺省值的参数，留空就代表不添加该模块.

    Args:
    - text: Section 中的文字
    - sub_text: Context 中的文字
    - img_url: 图片url（此处图片是和text在一起的，不是独立的图片）
    - card_color: 卡片边栏颜色
    - img_sz: 图片大小，只能为sm或者lg
    """
    c = Card(color=card_color)
    if img_url != 'e':
        c.append(
            Module.Section(Element.Text(text, Types.Text.KMD),
                           Element.Image(src=img_url, size=img_sz)))
    else:
        c.append(Module.Section(Element.Text(text, Types.Text.KMD)))
    if sub_text != 'e':
        c.append(Module.Context(Element.Text(sub_text, Types.Text.KMD)))

    return c


async def get_card_msg(text: str,
                       sub_text='e',
                       img_url='e',
                       card_color='#fb4b57',
                       img_sz='sm') -> CardMessage:
    """获取常用的卡片消息的卡片。有缺省值的参数，留空就代表不添加该模块.

    Args:
    - text: Section 中的文字
    - sub_text: Context 中的文字
    - img_url: 图片url（此处图片是和text在一起的，不是独立的图片）
    - card_color: 卡片边栏颜色
    - img_sz: 图片大小，只能为sm或者lg
    """
    cm = CardMessage()
    cm.append(await get_card(text, sub_text, img_url, card_color, img_sz))
    return cm


async def get_help_card_msg(err_text, help_text='', header_text='很抱歉，发生了一些错误'):
    """获取错误帮助卡片"""
    cm = CardMessage()
    c = Card(Module.Header(header_text))
    c.append(Module.Divider())
    c.append(Module.Section(err_text))
    if help_text != '':
        c.append(Module.Context(Element.Text(help_text, Types.Text.KMD)))
    c.append(Module.Divider())
    c.append(
        Module.Section(
            '有任何问题，请加入帮助服务器与我联系',
            Element.Button('帮助', 'https://kook.top/gpbTwZ', Types.Click.LINK)))
    cm.append(c)
    return cm
