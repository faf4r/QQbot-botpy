import os
import shutil
import zipfile
import json
import sqlite3
import time

tmp_dir = "temp_book_jsonl"

# step1 提取文件
def extract_zip(zip_path, extract_to=None):
    if extract_to is None:
        extract_to = os.path.dirname(zip_path)
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted {zip_path} to {extract_to}")


print("Extracting files...", end="")
os.makedirs(tmp_dir, exist_ok=True)
for filename in os.listdir('database/EnglishBook'):
    if not filename.endswith('.zip'):
        continue
    zip_path = os.path.join("database/EnglishBook", filename)
    extract_zip(zip_path, extract_to=tmp_dir)

# 因为文件实际为jsonl，改个名字
for filename in os.listdir(tmp_dir):
    if not filename.endswith('.jsonl'):
        continue
    os.rename(os.path.join(tmp_dir, filename), os.path.join(tmp_dir, filename[:-5] + '.jsonl'))
print("done.")


# step2 将数据写入数据库
print("Writing to database ./database/dict.db...")
conn = sqlite3.connect("database/dict.db")
with open("scripts/dict_schema.sql", encoding="utf-8") as f:
    conn.executescript(f.read())
    conn.commit()

"""
实际上比起使用这些高并发策略，注意不要每次写入
都commit就行了，最后所有写入完再commit或每个文
件commit一次，都能极大的提高性能，比使用这些策略还快
"""
# # 启用wal模式提升读写并发能力
# conn.execute("PRAGMA journal_mode=WAL")
# # 调整同步策略
# conn.execute("PRAGMA synchronous=NORMAL")
# # 调整缓存大小
# conn.execute("PRAGMA cache_size=-10000")  # 10MB缓存
# conn.commit()

def insert_word(wordId, word, book, usphone, ukphone, translation):
    conn.cursor().execute(
        """INSERT INTO words (wordId, word, book, usphone, ukphone, translation)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (wordId, word, book, usphone, ukphone, translation),
    )
    # conn.commit()


def insert_phrase(wordId, content, translation):
    conn.cursor().execute(
        """INSERT INTO phrases (wordId, content, translation)
        VALUES (?, ?, ?)""",
        (wordId, content, translation),
    )
    # conn.commit()

def insert_sentence(wordId, content, translation):
    conn.cursor().execute(
        """INSERT INTO sentences (wordId, content, translation)
        VALUES (?, ?, ?)""",
        (wordId, content, translation),
    )
    # conn.commit()

def insert_exam(wordId, question, answer, examType):
    conn.cursor().execute(
        """INSERT INTO exams (wordId, question, answer, examType)
        VALUES (?, ?, ?, ?)""",
        (wordId, question, answer, examType),
    )
    # conn.commit()


start_t = time.perf_counter()
files = os.listdir(tmp_dir)
total_all = len(files)
for cnt, filename in enumerate(files, 1):
    filename = os.path.join(tmp_dir, filename)
    print(f"processing {cnt}/{total_all} : {filename}")
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
        total = len(lines)
        for i, line in enumerate(lines, 1):
            print(f"\r{i}/{total}", end="")
            data = json.loads(line.strip())
            book = data["bookId"]
            data = data["content"]["word"]
            wordId = data["wordId"]
            word = data["wordHead"]
            trans = data["content"]["trans"]
            usphone = data["content"].get("usphone", "")
            ukphone = data["content"].get("ukphone", "")
            li = []
            for tran in trans:
                pos = tran.get("pos", "")
                if pos:
                    li.append(pos + ": " + tran["tranCn"])
                else:
                    li.append(tran["tranCn"])
            translation = "\n".join(li)
            insert_word(wordId, word, book, usphone, ukphone, translation)
            if data["content"].get("phrase", None):
                phrases = data["content"]["phrase"]["phrases"]
                for phrase in phrases:
                    content = phrase["pContent"]
                    translation = phrase["pCn"]
                    insert_phrase(wordId, content, translation)
            if data["content"].get("sentence", None):
                sentences = data["content"]["sentence"]["sentences"]
                for sentence in sentences:
                    content = sentence["sContent"]
                    translation = sentence["sCn"]
                    insert_sentence(wordId, content, translation)
            exams = data["content"].get("exam", None)
            if exams is not None:
                for exam in exams:
                    question = exam["question"]
                    choices = exam["choices"]
                    answer = exam["answer"]
                    for choice in choices:
                        question = (
                            question + f"\n{choice["choiceIndex"]}. {choice["choice"]}"
                        )
                    answer = f"{answer['rightIndex']}\n{answer['explain']}"
                    examType = "选择题"
                    insert_exam(wordId, question, answer, examType)
            exams = data["content"].get("realExamSentence", None)
            if exams is not None:
                exams = exams["sentences"]
                for exam in exams:
                    question = exam["sContent"]
                    examType = exam["sourceInfo"]["type"]
                    info = exam["sourceInfo"]
                    answer = f"{info['year']} {info['level']} {info['type']}"  # 标明出处，不是答案
                    insert_exam(wordId, question, answer, examType)
        conn.commit()
        print()
conn.close()
finish_t = time.perf_counter()
print(f"Finished in {finish_t - start_t:0.4f} seconds")
shutil.rmtree(tmp_dir)
