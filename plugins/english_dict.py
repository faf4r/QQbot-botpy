import sqlite3
import re
from utils import logger


def call_name():
    return ["/单词tag", "单词tag",
            "/记单词", "记单词", "/单词", "单词",
            "/exam", "exam", "/测验", "测验",
            "/answer", "answer", "/回答", "回答"]


async def botio(message, info, api):
    pending_word = info.setdefault("pending_words", {})
    english = EnglishDict()
    msg = message.content.strip()
    group_id = message.group_openid
    user_id = message.author.member_openid

    if msg.lower().split()[0] in ["/单词tag", "单词tag"]:
        return await message.reply(content=english.list_tags())
    elif msg.lower().split()[0] in ["/记单词", "记单词", "/单词", "单词"]:
        if len(msg.split()) == 1:
            content = english.random_word()
        elif len(msg.split()) == 2:
            arg = msg.split()[1]
            if arg.isdigit():
                num = int(arg)
                content = english.random_word(num=num)
            else:
                content = english.random_word(tag=arg)
        elif len(msg.split()) == 3:
            arg1, arg2 = msg.split()[1:]
            num = int(arg1) if arg1.isdigit() else arg2
            tag = arg1 if not arg1.isdigit() else arg2
            content = english.random_word(num=num, tag=tag)
        logger.info(content)
        return await message.reply(content=content)
    elif msg.lower().split()[0] in ["/exam", "exam", "/测验", "测验"]:
        if len(msg.split()) == 1:
            word, definition = english.get_word_with_definition()
            possible_answers = english.get_possible_answers(definition)
            pending_word.setdefault(group_id, {})[user_id] = (word, possible_answers)
            content = f"写出对应单词：\n{definition}"
        elif len(msg.split()) == 2:
            tag = msg.split()[1]
            if tag not in english.list_tags():
                return await message.reply(content=f"tag{tag}无效，请对照/单词tag查看可用tag")
            word, definition = english.get_word_with_definition(tag=tag)
            possible_answers = english.get_possible_answers(definition)
            pending_word.setdefault(group_id, {})[user_id] = (word, possible_answers)
            content = f"写出对应单词：\n{definition}"
        logger.info(content)
        return await message.reply(content=content)

    elif msg.lower().split()[0] in ["/answer", "answer", "/回答", "回答"]:
        if group_id not in pending_word or user_id not in pending_word[group_id]:
            return await message.reply(content="没有待回答的单词，使用/exam获取待测单词")
        if len(msg.split()) == 1:
            return await message.reply(content="请输入单词")
        usr_answer = msg.split()[1].lower()
        word, possible_answers = pending_word[group_id].pop(user_id)
        if usr_answer == word.lower():
            return await message.reply(content="回答正确！")
        elif usr_answer in possible_answers:
            return await message.reply(content=f"同义词，目标单词是：{word}")
        else:
            return await message.reply(content=f"回答错误，正确答案是：{word}")


class EnglishDict:
    DATABASE = "database/dict.db"
    tags = """/记单词可用的tag：
    KaoYan(默认)
    CET4
    CET6
    TOEFL
    IELTS
    GRE
    GMAT
    SAT
    BEC
    Level4
    Level8
    PEPXiaoXue
    ChuZhong
    PEPChuZhong
    WaiYanSheChuZhong
    GaoZhong
    PEPGaoZhong
    BeiShiGaoZhong"""

    def __init__(self):
        self.conn: sqlite3.Connection = sqlite3.connect(self.DATABASE)

    def __del__(self):
        self.close()

    def close(self):
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    def random_word(self, num: int=1, tag: str="KaoYan"):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT word, translation  FROM words WHERE book LIKE "%{tag}%" ORDER BY RANDOM() LIMIT {num}')
        result = cursor.fetchall()
        cursor.close()
        if not result:
            return f"没有找到与{tag}相关的单词"
        ret = []
        for word, translation in result:
            ret.append(word + '\n' + translation)
        return '\n\n'.join(ret)

    def list_tags(self):
        return self.tags

    def get_word_with_definition(self, tag: str = "KaoYan"):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT word, translation FROM words WHERE book LIKE "%{tag}%" ORDER BY RANDOM()')
        result = cursor.fetchone()
        cursor.close()
        if not result:
            return None, f"No words found for tag: {tag}"
        word, definition = result
        return word, definition

    def get_possible_answers(self, definition: str):
        match = re.compile(r'[\u4e00-\u9fa5]+')
        CHNs = match.findall(definition)
        possible_answers = set()
        cursor = self.conn.cursor()
        for CHN in CHNs:
            cursor.execute(f'SELECT word FROM words WHERE translation LIKE "%{CHN}%"')
            results = cursor.fetchall()
            for result in results:
                possible_answers.add(result[0].lower())
        cursor.close()
        print(possible_answers)
        return possible_answers


if __name__ == "__main__":
    eng = EnglishDict()
    print(eng.list_tags())
    print(eng.random_word(3, "CET4"))
    print(eng.get_word_with_definition("KaoYan"))
    print(eng.get_possible_answers("放弃"))
    eng.close()
