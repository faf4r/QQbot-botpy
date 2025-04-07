import os

import botpy
from botpy.message import GroupMessage
from botpy.errors import ServerError
from botpy import logging
from botpy.ext.cog_yaml import read

from utils import logger
from utils import get_short_url, post_group_file, post_c2c_file, encode_data, get_content_link
from types import MethodType  # 用于绑定方法到api实例上(不用这个参数要传self.api)
from plugins.news_cmd import jwc5news, xg5news
from plugins.status import get_status
from plugins.setu import get_setu_api
from plugins.chatbot import ChatBot
from plugins.english_dict import EnglishDict
from plugins.mianshiya import Mianshiya

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

menu = """命令列表：
/ping:  测试机器人是否在线
/status:查询服务器状态
/每日一题:  随机获取每日一题，每日4点更新
/随机题: 随机一道面试鸭的题，可加参数选择方向
/记单词: [num] [tag]随机单词，默认1个考研单词
/exam: [tag] 随机单词测验，默认考研单词
/answer: [word] 回答单词测验
/单词tag:  列出记单词可用的tags
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
        self.english = EnglishDict()
        self.mianshiya = Mianshiya()
        self.pending_word = {}  # 存储待回答的单词
        self.api.post_group_b64file = MethodType(post_group_file, self.api)
        self.api.post_c2c_b64file = MethodType(post_c2c_file, self.api)
        logger.info(f"{self.robot.name} is on ready!")

    async def close(self):
        self.english.close()
        self.mianshiya.close()
        for chatbot in self.chatbot_dict.values():
            await chatbot.close()
        return await super().close()

    async def handle_msg(self, message: GroupMessage):
        msg = message.content.strip()
        group_id = message.group_openid
        user_id = message.author.member_openid

        if msg in ['/ping', 'ping', 'test']:
            return await message.reply(content="pong!")

        elif msg in ['/menu', 'menu', '菜单', '/help', 'help', '帮助', '命令']:
            return await message.reply(content=menu)

        elif msg in ['/status', '/状态', '状态', 'status']:
            status_msg = await get_status()
            return await message.reply(content=status_msg)

        elif msg.lower().split()[0] in ["/单词tag", "单词tag"]:
            return await message.reply(content=self.english.list_tags())

        elif msg.lower().split()[0] in ["/记单词", "记单词", "/单词", "单词"]:
            if len(msg.split()) == 1:
                content = self.english.random_word()
            elif len(msg.split()) == 2:
                arg = msg.split()[1]
                if arg.isdigit():
                    num = int(arg)
                    content = self.english.random_word(num=num)
                else:
                    content = self.english.random_word(tag=arg)
            elif len(msg.split()) == 3:
                arg1, arg2 = msg.split()[1:]
                num = int(arg1) if arg1.isdigit() else arg2
                tag = arg1 if not arg1.isdigit() else arg2
                content = self.english.random_word(num=num, tag=tag)
            logger.info(content)
            return await message.reply(content=content)
        elif msg.lower().split()[0] in ["/exam", "exam", "/测验", "测验"]:
            if len(msg.split()) == 1:
                word, definition = self.english.get_word_with_definition()
                possible_answers = self.english.get_possible_answers(definition)
                self.pending_word.setdefault(group_id, {})[user_id] = (word, possible_answers)
                content = f"写出对应单词：\n{definition}"
            elif len(msg.split()) == 2:
                tag = msg.split()[1]
                if tag not in self.english.list_tags():
                    return await message.reply(content=f"tag{tag}无效，请对照/单词tag查看可用tag")
                word, definition = self.english.get_word_with_definition(tag=tag)
                possible_answers = self.english.get_possible_answers(definition)
                self.pending_word.setdefault(group_id, {})[user_id] = (word, possible_answers)
                content = f"写出对应单词：\n{definition}"
            logger.info(content)
            return await message.reply(content=content)

        elif msg.lower().split()[0] in ["/answer", "answer", "/回答", "回答"]:
            if group_id not in self.pending_word or user_id not in self.pending_word[group_id]:
                return await message.reply(content="没有待回答的单词，使用/exam获取待测单词")
            if len(msg.split()) == 1:
                return await message.reply(content="请输入单词")
            usr_answer = msg.split()[1].lower()
            word, possible_answers = self.pending_word[group_id].pop(user_id)
            if usr_answer == word.lower():
                return await message.reply(content="回答正确！")
            elif usr_answer in possible_answers:
                return await message.reply(content=f"同义词，目标单词是：{word}")
            else:
                return await message.reply(content=f"回答错误，正确答案是：{word}")

        elif msg.lower().split()[0] in ['/随机题', '随机题']:
            if len(msg.split()) == 1:
                content = await self.mianshiya.random_question()
            elif len(msg.split()) == 2:
                tag = msg.split()[1]
                try:
                    content = await self.mianshiya.random_question(tag)
                except ValueError as e:
                    logger.error(repr(e))
                    return await message.reply(content='参数异常')
            else:
                return await message.reply(content='参数过多')
            if content is None:
                return await message.reply(content='没有相关题目')
            logger.info(content)
            url, question = content.split('\n', 1)
            url = await get_short_url(url)
            content = f"{url}\n{question}"
            return await message.reply(content=content)

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

        elif msg.lower() in ['/ww', 'ww', '鸣潮']:
            raise NotImplementedError('未实现')

        elif msg.lower() in ["哒哒啦", "哒啦哒", "哒哒", "哒哒啦啦", "哒", "哒啦"]:
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

        elif msg.lower().split()[0] in ['/api', 'api']:
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
            try:
                return await message.reply(content=result)
            except ServerError as e:
                await message.reply(content="消息发送失败了")
                logger.warning(f"ServerError: {e.msgs}")
                link = await get_content_link(result, file_type=4)
                logger.info(f"转为消息链接：{link}")
                return await message.reply(content=f"请访问链接查看：{link}", msg_seq=2)

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


intents = botpy.Intents(public_messages=True, guild_messages=False)
client = MyClient(intents=intents, is_sandbox=False)
client.run(appid=config["appid"], secret=config["secret"])
