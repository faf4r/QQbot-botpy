import aiohttp
from io import BytesIO

lolicon_api = 'https://api.lolicon.app/setu/v2?size=regular'

async def lolicon_setu(tag_list=None):
    """
    根据tag进行请求获取图片，返回图片BytesIO, 图片链接, 原始请求结果
    """
    api = lolicon_api
    if tag_list is not None:
        api = lolicon_api + '&' + '&'.join(f"tag={s}" for s in tag_list)
    async with aiohttp.ClientSession() as session:
        async with session.get(api) as resp:
            result = await resp.json()
        if not result['data']:
            return None, None, result
        img_url = result['data'][0]['urls']['regular']
        async with session.get(img_url) as resp:
            img = BytesIO(await resp.read())
        return img, img_url, result


if __name__ == '__main__':
    import asyncio
    async def main():
        result = await lolicon_setu(tag_list=['安可'])
        print(result)
    asyncio.run(main())
