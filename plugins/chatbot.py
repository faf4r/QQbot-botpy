import asyncio

from openai import AsyncOpenAI
from botpy.ext.cog_yaml import read

config = read("config.yaml")
kimi= config["kimi"]
siliconflow = config["SiliconCloud"]
default_provider = kimi


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
