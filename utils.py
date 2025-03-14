from urllib.parse import quote
from botpy.ext.cog_yaml import read

config = read("config.yaml")


# 鉴于QQ机器人的限制，无法直接发送链接，因此用备案过的链接进行重定向
def redirect(url):
    redirect_url = config["redirect_url"]   # 备案过的域名，提供重定向服务
    if redirect_url:
        return redirect_url.format(quote(url))
    return url
