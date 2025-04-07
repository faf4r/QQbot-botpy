from urllib.parse import quote
from botpy.ext.cog_yaml import read

config = read("config.yaml")

# 短链接服务
# 鉴于QQ机器人的限制，无法直接发送链接，因此用备案过的链接进行重定向
import aiohttp
async def get_short_url(original_url):
    payload = {config["payload_field"]: original_url}
    async with aiohttp.ClientSession() as session:
        async with session.post(config["short_url"], json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"短链接服务异常: code {resp.status}")
            result = await resp.json()
    if result["success"] != 0:
        raise Exception(f"短链接服务异常: {result['message']}")
    return result["short_url"]


# 自定义日志文件路径
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from botpy.logging import configure_logging, get_logger

if not os.path.exists("logs"):
    os.mkdir("logs")

custom_handler = {
    "handler": TimedRotatingFileHandler,
    "format": "%(asctime)s\t[%(levelname)s]\t(%(filename)s:%(lineno)s)%(funcName)s\t%(message)s",
    "level": logging.DEBUG,
    "when": "D",
    "backupCount": 7,
    "encoding": "utf-8",
    "filename": os.path.join("logs", "%(name)s.log"),  # 日志文件存储在 logs 文件夹下
}

# 配置日志
configure_logging(ext_handlers=[custom_handler])

# 获取 logger
logger = get_logger("MyBot")


# 动态绑定方法到api实例上，实现本地文件上传
from botpy.types import message
from botpy.http import Route


async def post_group_file(
    self,
    group_openid: str,
    file_type: int,
    file_data: str,
    srv_send_msg: bool = False,
) -> message.Media:
    """
    上传/发送群聊图片

    Args:
        group_openid (str): 您要将消息发送到的群的 ID
        file_type (int): 媒体类型：1 图片png/jpg，2 视频mp4，3 语音silk，4 文件（暂不开放）
        file_data (str): 需要发送媒体资源的b64编码字符串
        srv_send_msg (bool): 设置 true 会直接发送消息到目标端，且会占用主动消息频次
    """
    payload = locals()
    payload.pop("self", None)
    route = Route("POST", "/v2/groups/{group_openid}/files", group_openid=group_openid)
    return await self._http.request(route, json=payload)


async def post_c2c_file(
    self,
    openid: str,
    file_type: int,
    file_data: str,
    srv_send_msg: bool = False,
) -> message.Media:
    """
    上传/发送c2c图片

    Args:
        openid (str): 您要将消息发送到的用户的 ID
        file_type (int): 媒体类型：1 图片png/jpg，2 视频mp4，3 语音silk，4 文件（暂不开放）
        file_data (str): 需要发送媒体资源的b64编码字符串
        srv_send_msg (bool): 设置 true 会直接发送消息到目标端，且会占用主动消息频次
    """
    payload = locals()
    payload.pop("self", None)
    route = Route("POST", "/v2/users/{openid}/files", openid=openid)
    return await self._http.request(route, json=payload)


from base64 import b64encode
from io import BytesIO

def encode_data(data: bytes | BytesIO | str) -> str:
    """
    对数据进行 Base64 编码
    :param data: 要编码的数据，可以是字节串或字符串
    :return: 编码后的字符串
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    elif isinstance(data, BytesIO):
        data = data.getvalue()
    return b64encode(data).decode()


async def get_content_link(content: bytes | BytesIO | str, file_type: int) -> str:
    """
    因内容被QQ拦截等原因发不出去，改为将内容上传服务器，获取链接进行访问
    :param content: 要获取链接的内容，可以是字符串或字节串
    :param file_type: 媒体类型：1 图片png/jpg，2 视频mp4，3 语音mp3，4 文本txt
    :return: 返回的链接
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    elif isinstance(content, BytesIO):
        content = content.getvalue()
    content = b64encode(content).decode()
    payload = locals()
    async with aiohttp.ClientSession() as session:
        async with session.post(config["content_upload"], json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"文件上传服务异常: code {resp.status}")
            result = await resp.json()
    if result["success"] != 0:
        raise Exception(f"文件上传服务异常: {result['message']}")
    return result["url"]
