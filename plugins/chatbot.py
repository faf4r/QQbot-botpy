from openai import OpenAI

from botpy.ext.cog_yaml import read

config = read("config.yaml")
kimi_key = config["kimi_key"]
kimi_url = config["kimi_url"]
kimi_model = config["kimi_model"]
sk_key = config["sk_key"]
sk_url = config["sk_url"]
sk_model = config["sk_model"]

client = OpenAI(
    api_key=kimi_key,
    base_url=kimi_url,
)

client_model = kimi_model
history = []


def chat(query):
    global history
    history.append({"role": "user", "content": query})
    completion = client.chat.completions.create(
        model=client_model,
        messages=history,
        temperature=0.3,
    )
    result = completion.choices[0].message.content
    history.append({"role": "assistant", "content": result})
    return result


def reset():
    global history
    history = []


def change_model(model):
    global client
    global client_model
    if model == "kimi":
        client = OpenAI(
            api_key=kimi_key,
            base_url=kimi_url,
        )
        client_model = kimi_model
    elif model == "deepseek":
        client = OpenAI(
            api_key=sk_key,
            base_url=sk_url,
        )
        client_model = sk_model


if __name__ == "__main__":
    reset("deepseek")
    print(chat("地球的自转周期是多少？"))
    print(chat("月球呢？"))
