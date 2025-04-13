import asyncio

from botpy.errors import ServerError
from botpy.ext.cog_yaml import read

from openai import AsyncOpenAI
from utils import logger, get_content_link

config = read("config.yaml")
kimi= config["kimi"]
siliconflow = config["SiliconCloud"]
default_provider = kimi


def call_name():
    return ['/reset', 'reset', '重置',
            '/model', 'model', '模型']


async def botio(message, info, api):
    msg = message.content.strip()
    chatbot_dict = info.setdefault("chatbot_dict", {})
    if msg.lower().split()[0] in ['/reset', 'reset', '重置']:
        chatbot = chatbot_dict.setdefault(message.group_openid, ChatBot())
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

        chatbot = chatbot_dict.setdefault(message.group_openid, None)
        if chatbot is None:
            chatbot = ChatBot(provider)
            chatbot_dict[message.group_openid] = chatbot
        else:
            chatbot.change_model(provider)
        logger.info(f"已切换模型为{provider}")
        return await message.reply(content=f"已切换模型为{provider['model']}")

    else:
        chatbot = chatbot_dict.setdefault(message.group_openid, ChatBot())
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


class ChatBot:
    system_prompt = {
        "role": "system",
        "content": "回答要尽量精简，仅提供问题的核心答案，避免不必要的细节,无特殊说明不要列举。尽量避免使用Markdown语法。回答中不得出现任何网址和链接。",
    }

    def __init__(self, provider=default_provider):
        self.client = AsyncOpenAI(
            api_key=provider['key'],
            base_url=provider['url'],
        )
        self.model = provider['model']
        self.history = [self.system_prompt]
        self.queue = asyncio.Queue()    # 使用队列保证异步请求的顺序
        self.processing_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            query, future = await self.queue.get()
            try:
                self.history.append({"role": "user", "content": query})
                completion = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                    temperature=0.3,
                )
                result = completion.choices[0].message.content
                self.history.append({"role": "assistant", "content": result})
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()

    async def chat(self, query):
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((query, future))
        return await future

    def reset(self):
        self.history = [self.system_prompt]

    def change_model(self, provider):
        self.client = AsyncOpenAI(
            api_key=provider['key'],
            base_url=provider['url'],
        )
        self.model = provider['model']
        self.history = [self.system_prompt]

    async def close(self):
        self.processing_task.cancel()
        try:
            await self.processing_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    import asyncio
    async def main():
        chatbot = ChatBot()
        chatbot.change_model(siliconflow['url'], siliconflow['key'], siliconflow['model'])
        a = asyncio.create_task(chatbot.chat("地球的自转周期是多少？"))
        b = asyncio.create_task(chatbot.chat("月球呢？"))
        await asyncio.gather(a, b)
        print(a.result())
        print(b.result())
        print(chatbot.history)
    # async def main():
    #     chatbot = ChatBot()
    #     chatbot.change_model(sk_url, sk_key, sk_model)
    #     a = await chatbot.chat("地球的自转周期是多少？")
    #     b = await chatbot.chat("月球呢？")
    #     print(a)
    #     print(b)
    #     print(chatbot.history)

    asyncio.run(main())
