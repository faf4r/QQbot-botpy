PRAGMA foreign_keys = ON;  -- 启用外键约束

CREATE TABLE IF NOT EXISTS words (
    wordId VARCHAR(30) PRIMARY KEY,
    word VARCHAR(256) NOT NULL,
    book VARCHAR(20) NOT NULL,      -- 如CET-4等
    usphone VARCHAR(20),            -- 美式音标
    ukphone VARCHAR(20),            -- 英式音标
    translation TEXT                -- 翻译
);

CREATE TABLE IF NOT EXISTS phrases (
    content TEXT NOT NULL,          -- 短语
    translation TEXT,               -- 翻译
    wordId VARCHAR(30),             -- 单词ID
    FOREIGN KEY (wordId) REFERENCES words(wordId)
);

CREATE TABLE IF NOT EXISTS sentences (
    content TEXT NOT NULL,          -- 句子
    translation TEXT,               -- 翻译
    wordId VARCHAR(30) NOT NULL,    -- 单词ID
    FOREIGN KEY (wordId) REFERENCES words(wordId)
);

CREATE TABLE IF NOT EXISTS exams (
    wordId VARCHAR(30) NOT NULL,    -- 单词ID
    question TEXT NOT NULL,         -- 题目
    answer TEXT,                    -- 答案
    examType VARCHAR(20),           -- 题目类型
    FOREIGN KEY (wordId) REFERENCES words(wordId)
);

CREATE INDEX IF NOT EXISTS idx_words_word ON words(word);
CREATE INDEX IF NOT EXISTS idx_wordId ON words(wordId);
CREATE INDEX IF NOT EXISTS idx_phrases_wordId ON phrases(wordId);
CREATE INDEX IF NOT EXISTS idx_sentences_wordId ON sentences(wordId);
CREATE INDEX IF NOT EXISTS idx_exams_wordId ON exams(wordId);
