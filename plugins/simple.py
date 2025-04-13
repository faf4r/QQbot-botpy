def call_name():
    return ['/ping', 'ping', 'test',
            '/menu', 'menu', '菜单', '/help', 'help', '帮助', '命令',
            '/ww', 'ww', '鸣潮']

menu = """命令列表：
/ping:  测试机器人是否在线
/status:查询服务器状态
/每日一题:  随机获取每日一题，每日4点更新
/随机题: 随机一道面试鸭的题，可加参数选择方向
/记单词: [num] [tag]随机单词，默认1个考研单词
/exam: [tag] 随机单词测验，默认考研单词
/answer: [word] 回答单词测验
/单词tag:  列出记单词可用的tags
/koyso: [game_name] 查询最新10个游戏，或搜索指定游戏
/jwc:   查询教务处通知
/xg:    查询学工处通知
/setu:  发送涩图(可加关键字，空格分隔)
/api:   切换涩图API
/reset: 重置对话
/model: 切换对话模型(kimi/silicon)
/menu:  菜单
"""


async def botio(message, info, api):
    msg = message.content.strip()
    if msg in ['/ping', 'ping', 'test']:
        return await message.reply(content="pong!")
    elif msg in ['/menu', 'menu', '菜单', '/help', 'help', '帮助', '命令']:
        return await message.reply(content=menu)
    elif msg.lower() in ['/ww', 'ww', '鸣潮']:
        raise NotImplementedError('未实现')
