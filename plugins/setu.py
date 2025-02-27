import requests
import json
from io import BytesIO

lolicon_api = 'https://api.lolicon.app/setu/v2?size=regular'

def lolicon_setu(tag_list=None):
    """
    根据tag进行请求获取图片，返回图片BytesIO, 图片链接, 原始请求结果
    """
    api = lolicon_api
    if tag_list is not None:
        api = lolicon_api + '&' + '&'.join(f"tag={s}" for s in tag_list)
    resp = requests.get(api)
    result = json.loads(resp.text)
    if not result['data']:
        return None, None, result
    img_url = result['data'][0]['urls']['regular']
    resp = requests.get(img_url)
    # with open('test.jpg', 'wb') as f:
    #     f.write(resp.content)
    img = BytesIO(resp.content)
    return img, img_url, result


if __name__ == '__main__':
    lolicon_setu(tag_list=['安可'])
