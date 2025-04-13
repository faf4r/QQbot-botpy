import os
import random

from botpy.errors import ServerError
from types import MethodType
from utils import post_group_file, post_c2c_file, encode_data, logger


def call_name():
    return ["哒哒啦", "哒啦哒", "哒哒", "哒哒啦啦", "哒", "哒啦",
            "鸣潮的小曲", "/鸣潮的小曲", "小曲"]


async def botio(message, info, api):
    msg = message.content.strip()
    api.post_group_b64file = MethodType(post_group_file, api)
    api.post_c2c_b64file = MethodType(post_c2c_file, api)
    wwmusic = [os.path.join('./database/wwmusic/', file) for file in os.listdir('./database/wwmusic/')]
    if msg.lower() in ["哒哒啦", "哒啦哒", "哒哒", "哒哒啦啦", "哒", "哒啦"]:
        try:
            with open('夏空.silk', 'rb') as f:
                data = f.read()
            media = await message._api.post_group_b64file(
                group_openid=message.group_openid,
                file_type=3,
                file_data=encode_data(data),
            )
            await message.reply(
                content="你说的对，但是",
                msg_seq=2,
            )
            return await message.reply(
                msg_type=7,
                msg_seq=3,
                media=media,
            )
        except ServerError as e:
            logger.warning(f"ServerError: {e.msgs}")
    elif msg.lower() in ["鸣潮的小曲", "/鸣潮的小曲", "小曲"]:
        try:
            fp = random.choice(wwmusic)
            logger.info(fp)
            with open(fp, 'rb') as f:
                data = f.read()
            title = fp.rsplit('/', 1)[-1].rstrip('.silk')
            media = await message._api.post_group_b64file(
                group_openid=message.group_openid,
                file_type=3,
                file_data=encode_data(data),
            )
            await message.reply(
                content=title,
                msg_seq=2,
            )
            return await message.reply(
                msg_type=7,
                msg_seq=3,
                media=media,
            )
        except ServerError as e:
            logger.warning(f"ServerError: {e.msgs}")
            await message.reply(content="消息发送失败")