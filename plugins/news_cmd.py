import requests
from lxml import etree

headers = {'User-Agent': 'Mozilla 5.0'}

def jwc5news():
    jwc_url = 'http://jwc.swjtu.edu.cn/vatuu/WebAction?setAction=newsList'
    resp = requests.get(url=jwc_url, headers=headers)
    html = etree.HTML(resp.text)
    items = html.xpath('/html/body/div[3]/div/div[1]/div')
    items = items[:5] if len(items) > 5 else items  # 仅展示最新5条消息
    msg = ""
    for i, item in enumerate(items):
        title = item.xpath('h3/a/text()')[0]
        link = item.xpath('h3/a/@href')[0]
        link = link.replace('../', 'http://jwc.swjtu.edu.cn/')
        link = 'https://qqbot.ltp.icu/redirect/' + link # 过审
        date = item.xpath('p/span[1]/text()')[0]
        msg += f'\n[{i+1}] ' + '\n'.join([title, date, link]) + '\n'
    return msg


def xg5news():
    xg_url = 'http://xg.swjtu.edu.cn/web/Home/PushNewsList?Lmk7LJw34Jmu=010j.shtml'
    resp = requests.get(url=xg_url, headers=headers)
    html = etree.HTML(resp.text)
    items = html.xpath('/html/body/div[3]/div/div[2]/div[2]/ul/li')
    items = items[:5] if len(items) > 5 else items  # 仅展示最新5条消息
    msg = ""
    for i, item in enumerate(items):
        title = item.xpath('h4/a/text()')[0]
        link = item.xpath('h4/a/@href')[0]
        link = 'http://xg.swjtu.edu.cn' + link
        link = 'https://qqbot.ltp.icu/redirect/' + link # 过审
        date = item.xpath('p/span[1]/text()')[0]
        msg += f'\n[{i+1}] ' + '\n'.join([title, date, link]) + '\n'
    return msg

if __name__ == '__main__':
    # msg = jwc5news()
    # print(msg)
    msg = xg5news()
    print(msg)