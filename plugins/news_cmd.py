import aiohttp
from lxml import etree

from utils import redirect  # 相对导入，utils与bot.py在同一目录下

headers = {'User-Agent': 'Mozilla 5.0'}

async def jwc5news():
    jwc_url = 'http://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList'
    async with aiohttp.ClientSession() as session:
        async with session.get(jwc_url, headers=headers) as resp:
            html = await resp.text()
    html = etree.HTML(html)
    items = html.xpath('/html/body/div[3]/div/div[1]/div')
    items = items[:5] if len(items) > 5 else items  # 仅展示最新5条消息
    msg = ""
    for i, item in enumerate(items):
        title = item.xpath('h3/a/text()')[0]
        link = item.xpath('h3/a/@href')[0]
        link = link.replace('../', 'http://jwc.swjtu.edu.cn/')
        link = redirect(link) # 过审
        date = item.xpath('p/span[1]/text()')[0]
        msg = f"\n[{i+1}] {'\n'.join([title, date, link])}\n{msg}"
    return msg


async def xg5news():
    xg_url = 'http://xg.swjtu.edu.cn/web/Home/PushNewsList?Lmk7LJw34Jmu=010j.shtml'
    async with aiohttp.ClientSession() as session:
        async with session.get(xg_url, headers=headers) as resp:
            html = await resp.text()
    html = etree.HTML(html)
    items = html.xpath('/html/body/div[3]/div/div[2]/div[2]/ul/li')
    items = items[:5] if len(items) > 5 else items  # 仅展示最新5条消息
    msg = ""
    for i, item in enumerate(items):
        title = item.xpath('h4/a/text()')[0]
        link = item.xpath('h4/a/@href')[0]
        link = 'http://xg.swjtu.edu.cn' + link
        link = redirect(link)  # 过审
        date = item.xpath('p/span[1]/text()')[0]
        msg = f"\n[{i+1}] {'\n'.join([title, date, link])}\n{msg}"
    return msg

if __name__ == '__main__':
    # msg = jwc5news()
    # print(msg)
    msg = xg5news()
    print(msg)
