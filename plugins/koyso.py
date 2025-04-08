from lxml import html
import requests
import re


def id_extractor(herf):
    match = re.search(r'/game/(\d+)', herf)
    print(match)
    return match.group(1) if match else None


def get_all_games(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        tree = html.fromstring(response.text)
        games = tree.xpath('//div[@class="games_content"]//a[@class="game_item"]')

        result = []
        for game in games[:10]:
            name = game.xpath('.//div[@class="game_info"]/span/text()')
            href = game.xpath('@href')[0] if game.xpath('@href') else None

            if name and href:
                game_id = id_extractor(href)
                if game_id:
                    new_url = f"https://s.ltp.icu/koyso/{game_id}"
                    result.append({
                        "name": name[0].strip(),
                        "new_url": new_url
                    })
        return result

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
        return []
    except Exception as e:
        print(f"解析错误: {str(e)}")
        return []


def format_games_string(games):
    if not games:
        return "没有找到游戏"

    output_lines = []
    for idx, game in enumerate(games, 1):
        output_lines.append(
            f"{idx}. {game['name']}\n"
            f"{game['new_url']}\n"
        )

    return "\n".join(output_lines)


def latest_games():
    target_url = "https://koyso.com/?sort=latest"
    games = get_all_games(target_url)
    ini_str = format_games_string(games)
    if ini_str != "没有找到游戏":
        output_str = "最新10个游戏:\n"+ini_str
        return output_str
    else:
        return ini_str


def search_games(game_name):
    target_url = "https://koyso.com/?keywords=" + str(game_name)
    games = get_all_games(target_url)
    ini_str = format_games_string(games)
    if ini_str != "没有找到游戏":
        output_str = "匹配到以下游戏:\n"+ini_str
        return output_str
    else:
        return ini_str


if __name__ == "__main__":
    print(latest_games())
    print(search_games("slave"))
