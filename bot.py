import os

import botpy
from botpy.message import GroupMessage
from botpy.errors import ServerError
from botpy import logging
from botpy.ext.cog_yaml import read

from plugins.news_cmd import jwc5news, xg5news
from plugins.status import get_status
from plugins.setu import get_setu_api
from plugins.chatbot import ChatBot
from utils import redirect
from utils import logger

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

menu = """命令列表：
/ping:  测试机器人是否在线
/status:查询服务器状态
/jwc:   查询教务处通知
/xg:    查询学工处通知
/setu:  发送涩图(可加关键字，空格分隔)
/api:   切换涩图API
/reset: 重置对话
/model: 切换对话模型(kimi/silicon)
/menu:  菜单
"""


class MyClient(botpy.Client):
    async def on_ready(self):
        self.chatbot_dict = {}  # 根据群组openid存储chatbot实例
        self.setu_api = {}      # 根据群组openid存储涩图API
        logger.info(f"{self.robot.name} is on ready!")

    async def handle_msg(self, message: GroupMessage):
        msg = message.content.strip()

        if msg in ['/ping', 'ping', 'test']:
            return await message.reply(content="pong!")

        elif msg in ['/menu', 'menu', '菜单', '/help', 'help', '帮助', '命令']:
            return await message.reply(content=menu)

        elif msg in ['/status', '/状态', '状态', 'status']:
            status_msg = await get_status()
            return await message.reply(content=status_msg)

        elif msg.lower() in ['/jwc', 'jwc', '教务处', 'news', '通知']:
            await message.reply(content='查询中...', msg_seq=1)
            jwc_news = await jwc5news()
            logger.info(jwc_news)
            return await message.reply(content=jwc_news, msg_seq=2)

        elif msg.lower() in ['/xg', 'xg', '学工']:
            await message.reply(content='查询中...', msg_seq=1)
            xg_news = await xg5news()
            logger.info(xg_news)
            return await message.reply(content=xg_news, msg_seq=2)

        elif msg.lower().split()[0] in ['/api', 'api']:
            txt = msg.lower().split()[1:]
            if not txt:
                return await message.reply(
                    content="请指定API名称：\n\tlolicon\n\tltp\n\审核"
                )
            name = txt[0]
            if name in ["lolicon", "loli", "萝莉"]:
                name = "lolicon"
            elif name in ["ltp"]:
                name = "ltp"
            elif name in ["审核", "shenhe"]:
                name = "shenhe"
            else:
                return await message.reply(
                    content="目前支持的api有：lolicon, ltp, 审核"
                )
            self.setu_api[message.group_openid] = get_setu_api(name)
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
            get_setu = self.setu_api.setdefault(message.group_openid, get_setu_api())
            img, img_url, result = await get_setu(tag_list=tag_list)
            logger.debug(result)
            logger.info(img_url)
            if img_url is None:
                return await message.reply(result['error'], msg_seq=2)
            try:
                media = await message._api.post_group_file(
                    group_openid=message.group_openid,
                    file_type=1,
                    url=img_url
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
                return await message.reply(
                    content=f"请直接访问链接查看~：{redirect(img_url)}", msg_seq=3
                )
            except Exception as e:
                logger.error(e.__repr__())
                logger.error(f"Exception type: {type(e).__name__}, Exception message: {str(e)}")
                await message.reply(
                    content=f"未知错误\n涩图发送失败了>.<", msg_seq=2
                )
                return await message.reply(
                    content=f"请直接访问链接查看~：{redirect(img_url)}", msg_seq=3
                )

        elif msg.lower().split()[0] in ['/reset', 'reset', '重置']:
            chatbot = self.chatbot_dict.setdefault(message.group_openid, ChatBot())
            chatbot.reset()
            logger.info("reset done.")
            return await message.reply(content="已开启新的对话~")

        elif msg.lower().split()[0] in ['/model', 'model', '模型']:
            txt = msg.lower().split()[1:]
            if not txt:
                return await message.reply(
                    content="请指定模型供应商：\n\tkimi: moonshot-v1-8k\n\tsiliconflow: deepseek-ai/DeepSeek-V3"
                )
            provider = txt[0]
            if provider in ['kimi']:
                provider = config['kimi']
            elif provider in ['siliconflow', '硅基流动', 'silicon']:
                provider = config['SiliconCloud']
            else:
                return await message.reply(content="目前支持的供应商有：kimi, siliconflow")

            chatbot = self.chatbot_dict.setdefault(message.group_openid, None)
            if chatbot is None:
                chatbot = ChatBot(provider)
                self.chatbot_dict[message.group_openid] = chatbot
            else:
                chatbot.change_model(provider)
            logger.info(f"已切换模型为{provider}")
            return await message.reply(content=f"已切换模型为{provider['model']}")

        else:
            chatbot = self.chatbot_dict.setdefault(message.group_openid, ChatBot())
            result = await chatbot.chat(msg)
            logger.info(result)
            logger.debug(chatbot.history)
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
client = MyClient(intents=intents, is_sandbox=False)
client.run(appid=config["appid"], secret=config["secret"])
