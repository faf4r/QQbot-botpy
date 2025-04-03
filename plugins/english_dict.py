import sqlite3
import re


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

    def get_word_with_definition(self, num: int = 1, tag: str = "KaoYan"):
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT word, translation FROM words WHERE book LIKE "%{tag}%" ORDER BY RANDOM() LIMIT {num}')
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
                possible_answers.add(result[0])
        cursor.close()
        return list(possible_answers)


if __name__ == "__main__":
    eng = EnglishDict()
    print(eng.list_tags())
    print(eng.random_word(3, "CET4"))
    print(eng.get_word_with_definition(1, "KaoYan"))
    print(eng.get_possible_answers("放弃"))
    eng.close()
