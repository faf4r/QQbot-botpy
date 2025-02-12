import botpy
from botpy import logging
from botpy.message import GroupMessage

from botpy.ext.cog_yaml import read
import os
config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

import asyncio
import psutil
from datetime import datetime

from plugins.news_cmd import jwc5news, xg5news
from plugins.setu import lolicon_setu, lizi_setu
from plugins.chatbot import chat, reset, change_model

logger = logging.get_logger()

def _get_disk_usage(path: str):
    try:
        return psutil.disk_usage(path)
    except Exception as e:
        logger.warning(f"Could not get disk usage for {path}: {e!r}")


def get_disk_usage():
    """Get the disk usage status."""
    disk_parts = psutil.disk_partitions()
    return {
        d.mountpoint: usage.percent
        for d in disk_parts
        if (usage := _get_disk_usage(d.mountpoint))
    }

async def get_status():
    """Get the server usage status."""
    psutil.cpu_percent()
    await asyncio.sleep(0.5)
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    disk = get_disk_usage()
    disk = '\n'.join(f"\t\t\t\t{k}\t\t{v}%" for k,v in disk.items())
    status_msg = f"\nCPU usage: {cpu}%\nMemory usage: {mem}%\ndisk usage: \n{disk}"
    return status_msg

async def get_lolicon_setu(message: GroupMessage):
    await message.reply(content='请求中...', msg_seq=1)
    keywords = message.content.strip().split()
    if len(keywords) > 1:
        tag_list = keywords[1:]
    else:
        tag_list = None
    logger.info('请求中...')
    img, img_url, result = lolicon_setu(tag_list=tag_list)
    logger.info(result)
    logger.info(img_url)
    if img_url is None:
        return await message.reply(result['error'])
    media = await message._api.post_group_file(
        group_openid=message.group_openid,
        file_type=1,
        url=img_url
    )
    return await message.reply(
        msg_type=7,
        msg_seq=2,
        content="你要的涩图~",
        media=media,
    )

async def get_lizi_setu(message: GroupMessage):
    # await message.reply(content='请求中...', msg_seq=1)
    img_url = lizi_setu()
    logger.info(img_url)
    media = await message._api.post_group_file(
        group_openid=message.group_openid,
        file_type=1,
        url=img_url
    )
    return await message.reply(
        msg_type=7,
        msg_seq=2,
        content="你要的涩图~",
        media=media,
    )

class MyClient(botpy.Client):
    async def on_ready(self):
        #TODO: 启动其它服务的线程以供使用
        logger.info(f"{self.robot.name} is on ready!")

    async def send_status(self, message: GroupMessage):
        status_msg = await get_status()
        return await message.reply(content=status_msg)

    async def handle_msg(self, message: GroupMessage):
        msg = message.content.strip()
        if msg in ['/ping', 'ping', 'test']:
            return await message.reply(content="pong!")
        elif msg in ['/status', '/状态', '状态', 'status']:
            return await self.send_status(message)
        elif msg.lower() in ['/jwc', 'jwc', '教务处', 'news', '通知']:
            await message.reply(content='查询中...', msg_seq=1)
            jwc_news = jwc5news()
            logger.info(jwc_news)
            return await message.reply(content=jwc_news, msg_seq=2)
        elif msg.lower() in ['/xg', 'xg', '学工']:
            await message.reply(content='查询中...', msg_seq=1)
            xg_news = xg5news()
            logger.info(xg_news)
            return await message.reply(content=xg_news, msg_seq=2)
        elif msg.lower().split()[0] in ['/setu', 'setu', '涩', '涩图', '涩涩', '色']:
            # return await get_lolicon_setu(message)
            return await get_lizi_setu(message)
        elif msg.lower().split()[0] in ['/reset', 'reset', '重置']:
            reset()
            logger.info("reset done.")
            return await message.reply(content="已开启新的对话~")
        elif msg.lower().split()[0] in ['/model', 'model', '模型']:
            txt = msg.lower().split()[1:]
            if not txt:
                return await message.reply(content="请指定模型名称\n目前支持的模型有：kimi, deepseek")
            model = txt[0]
            if model not in ['kimi', 'deepseek']:
                return await message.reply(content="目前支持的模型有：kimi, deepseek")
            change_model(model)
            logger.info(f"已切换模型为{model}")
            return await message.reply(content=f"已切换模型为{model}")
        else:
            result = chat(msg)
            logger.info(result)
            return await message.reply(content=result)

    async def on_group_at_message_create(self, message: GroupMessage):
        """
        当接收到群内at机器人的消息
        """
        logger.info(f"收到：{message.content}")
        msg_result = await self.handle_msg(message)
        logger.debug(msg_result)
    
    async def on_message_create(self, message: GroupMessage):
        """
        当接收到频道内全部消息
        """
        logger.info(f"收到：{message.content}")
        msg_result = await message.reply(content=f"received: {message.content}")
        logger.debug(msg_result)

intents = botpy.Intents(public_messages=True, guild_messages=True) 
client = MyClient(intents=intents, is_sandbox=True)
client.run(appid=config['appid'], secret=config['secret'])
