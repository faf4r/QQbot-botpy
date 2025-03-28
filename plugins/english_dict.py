import sqlite3


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
        self.conn.close()

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


if __name__ == "__main__":
    eng = EnglishDict()
    print(eng.list_tags())
    print(eng.random_word(3, "CET4"))
    eng.close()
