import os
import importlib

import botpy
from botpy.message import GroupMessage
from botpy.ext.cog_yaml import read

from utils import logger

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))


class MyClient(botpy.Client):
    async def on_ready(self):
        self.info = {}  # pending_words, chatbot_dict, setu_api
        self.call_name_dict = {}
        plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"plugins.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    if hasattr(module, "call_name") and callable(module.call_name):
                        self.call_name_dict[filename[:-3]] = module.call_name()
                        logger.info(f"Loaded module: {filename[:-3]}")
                except Exception as e:
                    logger.error(f"Failed to load {module_name}: {e}")

        logger.info(f"Loaded call_name results: {self.call_name_dict}")
        logger.info(f"{self.robot.name} is on ready!")


    async def handle_msg(self, message: GroupMessage):
        call_word = message.content.strip().lower().split()[0]
        for module_name, call_names in self.call_name_dict.items():
            if call_word in call_names:
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "botio") and callable(module.botio):
                    return await module.botio(message, self.info, self.api)
        module = importlib.import_module("plugins.chatbot")
        return await module.botio(message, self.info, self.api)



    async def on_group_at_message_create(self, message: GroupMessage):
        """
        当接收到群内at机器人的消息
        """
        logger.info(f"收到：{message.content}")
        msg_result = await self.handle_msg(message)
        logger.debug(msg_result)

    async def on_message_create(self, message: GroupMessage):
        """
        当接收到频道内全部消息
        """
        logger.info(f"收到：{message.content}")
        msg_result = await message.reply(content=f"received: {message.content}")
        logger.debug(msg_result)


intents = botpy.Intents(public_messages=True, guild_messages=False)
client = MyClient(intents=intents, is_sandbox=False, timeout=60)
client.run(appid=config["appid"], secret=config["secret"])
