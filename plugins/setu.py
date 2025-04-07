import aiohttp
from io import BytesIO


async def lolicon_setu(tag_list=None):
    """
    根据tag进行请求获取图片，返回图片BytesIO, 图片链接, 原始请求结果
    """
    api = "https://api.lolicon.app/setu/v2?size=regular"
    if tag_list is not None:
        api = api + '&' + '&'.join(f"tag={s}" for s in tag_list)
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            result = await resp.json()
        if not result['data']:
            return None, None, result
        img_url = result['data'][0]['urls']['regular']
        async with session.get(img_url) as resp:
            if resp.status != 200:
                return None, None, {"error": "status error", "result": result}
            img = BytesIO(await resp.read())
        return img, img_url, result


async def lolicon_noAI_setu(tag_list=None):
    """
    因setu上传策略变动，该方法已不需要了，直接作为排除AI的lolicon API
    """
    api = "https://api.lolicon.app/setu/v2?size=regular&excludeAI=true"
    if tag_list is not None:
        api = api + "&" + "&".join(f"tag={s}" for s in tag_list)
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            result = await resp.json()
        if not result["data"]:
            return None, None, result
        img_url = result["data"][0]["urls"]["regular"]
        async with session.get(img_url) as resp:
            if resp.status != 200:
                return None, None, {"error": "status error", "result": result}
            img = BytesIO(await resp.read())
        return img, img_url, result


async def shenhe_setu(tag_list=None):
    """
    专门审核用的能过审图片(非setu)
    """
    api = "https://picsum.photos/600"
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            img = BytesIO(await resp.read())
            img_url = str(resp.url)
        return img, img_url, {"error": "好像出错了捏~"}  # error信息无效，需要读取时当做发生错误


def get_setu_api(name=None):
    if name is None:
        return lolicon_setu
    if name == 'lolicon':
        return lolicon_setu
    elif name == "lolicon_noAI":
        return lolicon_noAI_setu
    elif name == 'shenhe':
        return shenhe_setu
    else:
        return lolicon_setu


if __name__ == '__main__':
    import asyncio
    async def main():
        result = await lolicon_setu(tag_list=['安可'])
        print(result)
    asyncio.run(main())
