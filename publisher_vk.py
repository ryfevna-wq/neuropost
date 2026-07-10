"""
НейроПост v2.0 — Модуль 4: Публикация в VK
"""
import argparse
import os
import sys
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

VK_API_URL = "https://api.vk.com/method"
VK_API_VERSION = "5.131"


def read_post_file(filepath):
    if not os.path.exists(filepath):
        print(f"\n❌ Файл не найден: {filepath}\n")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "─" * 10 in content:
        parts = content.split("─" * 10, 1)
        post_text = parts[1].strip() if len(parts) > 1 else content.strip()
    else:
        post_text = content.strip()

    lines = post_text.split("\n")
    filtered = [l for l in lines if not l.startswith("ПРОМПТ ДЛЯ ВИЗУАЛА:")]
    return "\n".join(filtered).strip()


def publish_to_vk(text, token, group_id, publish_date=None):
    params = {
        "access_token": token,
        "v": VK_API_VERSION,
        "owner_id": f"-{group_id}",
        "message": text,
        "from_group": 1,
    }

    if publish_date:
        params["publish_date"] = int(publish_date.timestamp())

    try:
        response = requests.post(f"{VK_API_URL}/wall.post", data=params, timeout=30)
        result = response.json()

        if "error" in result:
            error_msg = result["error"].get("error_msg", "Неизвестная ошибка")
            print(f"\n❌ Ошибка VK API: {error_msg}\n")
            sys.exit(1)

        post_id = result["response"]["post_id"]
        print(f"\n✅ Пост опубликован в VK! ID поста: {post_id}")
        print(f"   Ссылка: https://vk.com/wall-{group_id}_{post_id}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Ошибка сети: {e}\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Публикация поста в VK")
    parser.add_argument("--file", required=True, help="Путь к файлу с постом")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--now", action="store_true", help="Опубликовать сейчас")
    group.add_argument("--time", help="Время публикации ЧЧ:ММ (сегодня)")
    args = parser.parse_args()

    vk_token = os.getenv("VK_TOKEN")
    vk_group_id = os.getenv("VK_GROUP_ID")

    if not vk_token or not vk_group_id:
        print("\n❌ VK_TOKEN и VK_GROUP_ID должны быть в .env файле\n")
        sys.exit(1)

    post_text = read_post_file(args.file)

    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — Публикация в VK")
    print("─" * 50)
    print(f"\nГруппа ID: {vk_group_id}")
    print(f"Файл: {args.file}")

    if args.now:
        print("Публикую сейчас...")
        publish_to_vk(post_text, vk_token, vk_group_id)
    else:
        try:
            target_time = datetime.strptime(args.time, "%H:%M")
            now = datetime.now()
            target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0)

            if target <= now:
                target += timedelta(days=1)

            print(f"⏰ Планирую публикацию на {args.time}...")
            publish_to_vk(post_text, vk_token, vk_group_id, publish_date=target)
        except ValueError:
            print(f"\n❌ Неверный формат времени. Используй ЧЧ:ММ, например: 10:30\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
