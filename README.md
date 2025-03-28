# Description
这个项目是一个基于QQ机器人框架的聊天机器人，具备多种功能，包括获取学校通知、随机图片以及与kimi进行对话。以下是项目的主要功能介绍：

- /ping:  测试机器人是否在线
- /status:查询服务器状态
- /随机题: 随机获取一道mianshiya的题，可加参数选择方向
- /记单词: [num] [tag]随机单词，默认1个KaoYan单词
- /单词tag:  列出记单词可用的tags
- /jwc:   查询教务处通知
- /xg:    查询学工处通知
- /setu:  发送涩图(可加关键字，空格分隔)
- /api:   切换涩图API
- /reset: 重置对话
- /model: 切换对话模型(kimi/silicon)
- /menu:  菜单

项目的主要文件和目录结构如下：
- bot.py：主程序文件，包含机器人客户端的实现和消息处理逻辑。
- plugins：插件目录，包含新闻获取、图片发送和聊天功能的实现。
- database: 数据库目录，包含数据库文件的存储。
- scripts: 脚本目录，包含一些辅助脚本，如数据库初始化脚本。
- config.yaml：配置文件，包含机器人API的配置信息。
- requirements.txt：依赖文件，列出了项目所需的Python库。

# Usage
- 在QQ机器人开发平台配置沙箱、白名单等
- 使用`pip install -r requirements.txt`安装`requirements.txt`中列出的依赖。
- 配置好`config.yaml`文件(参照`example.config.yaml`创建`config.yaml`)
- 使用`python3 bot.py`运行`bot.py`来启动这个机器人。
- @机器人发送`/menu`获取菜单

## 记单词功能数据库配置
在当前目录下执行`python3 scripts/dict_extract.py`即可
> 因为dict.db超过github限制的100MB，
> 所以上传了原始数据`database/EnglishBook`(来自https://github.com/kajweb/dict)，
> 执行脚本将生成`database/dict.db`，之后可选择是否删除`database/EnglishBook`

# TODO
- [ ] `plugins/chatbot.py`中的`_process_queue`存在问题，进行对话(即调用`chat`)时会出现`Task was destroyed but it is pending!`的报错，不过并不影响程序运行，不保证长久运行不出问题。