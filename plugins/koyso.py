from lxml import html
from utils import logger, get_short_url
import aiohttp
import asyncio


async def get_all_games(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                text = await response.text()

        tree = html.fromstring(text)
        games = tree.xpath('//div[@class="games_content"]//a[@class="game_item"]')

        result = []
        for game in games[:10]:
            name = game.xpath('.//div[@class="game_info"]/span/text()')
            href = game.xpath('@href')[0] if game.xpath('@href') else None

            if name and href:
                koyso_url = f"https://koyso.com{href}"
                short_url = await get_short_url(koyso_url)
                result.append({
                    "name": name[0].strip(),
                    "new_url": short_url
                })
        return result

    except aiohttp.ClientError as e:
        logger.info(f"网络请求失败: {str(e)}")
        return []
    except Exception as e:
        logger.info(f"解析错误: {str(e)}")
        return []


async def format_games_string(games):
    if not games:
        return "没有找到游戏"

    output_lines = []
    for idx, game in enumerate(games, 1):
        output_lines.append(
            f"{idx}. {game['name']}\n"
            f"{game['new_url']}\n"
        )

    return "\n".join(output_lines)


async def latest_games():
    target_url = "https://koyso.com/?sort=latest"
    games = await get_all_games(target_url)
    ini_str = await format_games_string(games)
    if ini_str != "没有找到游戏":
        output_str = "最新10个游戏:\n"+ini_str
        return output_str
    else:
        return ini_str


async def search_games(game_name):
    target_url = "https://koyso.com/?keywords=" + str(game_name)
    games = await get_all_games(target_url)
    ini_str = await format_games_string(games)
    if ini_str != "没有找到游戏":
        output_str = "匹配到以下游戏:\n"+ini_str
        return output_str
    else:
        return ini_str


if __name__ == "__main__":
    print(asyncio.run(latest_games()))
    print(asyncio.run(search_games("truck")))
