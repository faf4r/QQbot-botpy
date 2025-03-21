from urllib.parse import quote
from botpy.ext.cog_yaml import read

config = read("config.yaml")


# 鉴于QQ机器人的限制，无法直接发送链接，因此用备案过的链接进行重定向
def redirect(url):
    redirect_url = config["redirect_url"]   # 备案过的域名，提供重定向服务
    if redirect_url:
        return redirect_url.format(quote(url))
    return url


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
