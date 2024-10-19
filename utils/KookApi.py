import json
import aiohttp
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
            print(f"[Option 2] Update_ch:{ret1['message']} - ch:{channel_id}")
