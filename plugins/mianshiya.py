import sqlite3
import asyncio


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
