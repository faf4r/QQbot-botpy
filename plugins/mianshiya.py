import sqlite3
import asyncio
from botpy import logging
from utils import get_short_url, get_logger, logger


def call_name():
    return ['/随机题', '随机题']


async def botio(message, info, api):
    msg = message.content.strip()
    mianshiya = Mianshiya()
    if msg.lower().split()[0] in ['/随机题', '随机题']:
        if len(msg.split()) == 1:
            content = await mianshiya.random_question()
        elif len(msg.split()) == 2:
            tag = msg.split()[1]
            try:
                content = await mianshiya.random_question(tag)
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


class Mianshiya:
    DATABASE = "database/mianshiya.db"

    def __init__(self):
        self.conn = sqlite3.connect(self.DATABASE)
    
    def __del__(self):
        self.close()

    def close(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    async def random_question(self, tag: str=None):
        if tag is None:
            cursor = self.conn.execute("SELECT content, url FROM questions ORDER BY RANDOM() LIMIT 1")
        else:
            if len(tag) > 10:
                raise ValueError(f"Tag too long: {tag}")
            cursor = self.conn.execute(f'SELECT content, url FROM questions WHERE tags LIKE "%{tag}%" ORDER BY RANDOM() LIMIT 1')
        result = cursor.fetchone()
        if result is None:
            return None
        content, url = result
        return f"{url}\n{content}"


if __name__ == "__main__":
    async def main():
        obj = Mianshiya()
        result = await obj.random_question("Java")
        print(result)
        # obj.close()
    asyncio.run(main())
