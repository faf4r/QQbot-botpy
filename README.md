# Description
这个项目是一个基于QQ机器人框架的聊天机器人，具备多种功能，包括获取学校通知、随机图片以及与kimi进行对话。以下是项目的主要功能介绍：

1. **获取通知**：
   - 从教务处网站获取最新的5条新闻，使用`/jwc5news`命令。
   - 从学工网站获取最新的5条新闻，使用`/xg5news`命令。

2. **随机图片**：
   - 从lolicon API获取图片，使用`/setu`命令。
   - 指令可指定关键字，使用空格分隔。

3. **聊天功能**：
   - 使用kimi和硅基流动提供的API与用户进行对话。
   - 支持重置对话历史和模型切换。

4. **系统状态监控**：
   - 获取服务器的CPU、内存和磁盘使用情况，使用`/status`命令。

项目的主要文件和目录结构如下：
- bot.py：主程序文件，包含机器人客户端的实现和消息处理逻辑。
- plugins：插件目录，包含新闻获取、图片发送和聊天功能的实现。
- config.yaml：配置文件，包含机器人API的配置信息。
- requirements.txt：依赖文件，列出了项目所需的Python库。

# Usage
你可以通过运行`bot.py`来启动这个机器人。确保在运行前配置好`config.yaml`文件(参照`example.config.yaml`创建`config.yaml`)，并安装`requirements.txt`中列出的依赖。

# TODO
- [ ] `plugins/chatbot.py`中的`_process_queue`存在问题，进行对话(即调用`chat`)时会出现`Task was destroyed but it is pending!`的报错，不过并不影响程序运行，不保证长久运行不出问题。