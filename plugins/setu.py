import aiohttp
from io import BytesIO
from botpy.errors import ServerError
from types import MethodType
from utils import post_group_file, post_c2c_file, encode_data, logger, get_content_link


def call_name():
    return ['/api', 'api',
            '/setu', 'setu', '涩', '涩图', '涩涩', '色']


async def botio(message, info, api):
    msg = message.content.strip()
    setu_api = info.setdefault("setu_api", {})
    api.post_group_b64file = MethodType(post_group_file, api)
    api.post_c2c_b64file = MethodType(post_c2c_file, api)
    if msg.lower().split()[0] in ['/api', 'api']:
        txt = msg.lower().split(' ', 1)[1:]
        if not txt:
            return await message.reply(
                content="请指定API名称：\n\tlolicon\n\tno ai\n\t审核"
            )
        name = txt[0]
        if name in ["lolicon", "loli", "萝莉"]:
            name = "lolicon"
        elif name in ["noai", "no ai", "无ai", "lolicon_noAI"]:
            name = "lolicon_noAI"
        elif name in ["审核", "shenhe"]:
            name = "shenhe"
        else:
            return await message.reply(
                content="目前支持的api有：lolicon, no ai, 审核"
            )
        setu_api[message.group_openid] = get_setu_api(name)
        logger.info(f"已切换API为{name}")
        return await message.reply(content=f"已切换API为{name}")

    elif msg.lower().split()[0] in ['/setu', 'setu', '涩', '涩图', '涩涩', '色']:
        await message.reply(content='请求中...', msg_seq=1)
        keywords = message.content.strip().split()
        if len(keywords) > 1:
            tag_list = keywords[1:]
        else:
            tag_list = None
        logger.debug('setu请求中...')
        get_setu = setu_api.setdefault(message.group_openid, get_setu_api())
        img, img_url, result = await get_setu(tag_list=tag_list)
        logger.debug(result)
        logger.info(img_url)
        if img_url is None:
            if result.get('error') == 'status error':
                return await message.reply(content="图片404，请重新请求>.<", msg_seq=2)
            else:
                return await message.reply(content="找不到相关的图片>.<", msg_seq=2)
        try:
            media = await message._api.post_group_b64file(
                group_openid=message.group_openid,
                file_type=1,
                file_data=encode_data(img)
            )
            return await message.reply(
                msg_seq=2,
                msg_type=7,
                content="你要的涩图~",
                media=media,
            )
        except ServerError as e:
            logger.warning(f"ServerError: {e.msgs}")
            await message.reply(
                content=f"ServerError\n涩图发送失败了>.<", msg_seq=2
            )
            # await message.reply(
            #     content=f"请直接访问链接查看~：{await get_short_url(img_url)}", msg_seq=3
            # )
            cache_link = await get_content_link(img, file_type=1)
            logger.info(f"转为消息链接：{cache_link}")
            return await message.reply(
                content=f"请直接访问链接查看：{cache_link}", msg_seq=4)
        except Exception as e:
            logger.error(e.__repr__())
            logger.error(f"Exception type: {type(e).__name__}, Exception message: {str(e)}")
            await message.reply(
                content=f"未知错误\n涩图发送失败了>.<", msg_seq=2
            )
            # await message.reply(
            #     content=f"请直接访问链接查看~：{await get_short_url(img_url)}", msg_seq=3
            # )
            cache_link = await get_content_link(img, file_type=1)
            logger.info(f"转为消息链接：{cache_link}")
            return await message.reply(
                content=f"请直接访问链接查看：{cache_link}", msg_seq=4)


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
