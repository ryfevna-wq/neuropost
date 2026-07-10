"""
НейроПост v2.0 — Модуль 3: Публикация в Telegram
"""
import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


def read_post_file(filepath):
    if not os.path.exists(filepath):
        print(f"\n❌ Файл не найден: {filepath}\n")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Извлекаем текст после разделителя
    if "─" * 10 in content:
        parts = content.split("─" * 10, 1)
        if len(parts) > 1:
            post_text = parts[1].strip()
        else:
            post_text = content.strip()
    else:
        post_text = content.strip()

    # Убираем строку с промптом для визуала
    lines = post_text.split("\n")
    filtered = [l for l in lines if not l.startswith("ПРОМПТ ДЛЯ ВИЗУАЛА:")]
    return "\n".join(filtered).strip()


async def send_to_telegram(text, bot_token, channel_id):
    try:
        from telegram import Bot
        from telegram.error import TelegramError
    except ImportError:
        print("\n❌ Установи библиотеку: pip install python-telegram-bot\n")
        sys.exit(1)

    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=channel_id, text=text, parse_mode=None)
        print("\n✅ Пост опубликован в Telegram!")
    except Exception as e:
        print(f"\n❌ Ошибка публикации: {e}\n")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Публикация поста в Telegram")
    parser.add_argument("--file", required=True, help="Путь к файлу с постом")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--now", action="store_true", help="Опубликовать сейчас")
    group.add_argument("--time", help="Время публикации ЧЧ:ММ (сегодня)")
    args = parser.parse_args()

    bot_token = os.getenv("TG_BOT_TOKEN")
    channel_id = os.getenv("TG_CHANNEL_ID")

    if not bot_token or not channel_id:
        print("\n❌ TG_BOT_TOKEN и TG_CHANNEL_ID должны быть в .env файле\n")
        sys.exit(1)

    post_text = read_post_file(args.file)

    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — Публикация в Telegram")
    print("─" * 50)
    print(f"\nКанал: {channel_id}")
    print(f"Файл: {args.file}")

    if args.now:
        print("Публикую сейчас...")
        asyncio.run(send_to_telegram(post_text, bot_token, channel_id))
    else:
        try:
            target_time = datetime.strptime(args.time, "%H:%M")
            now = datetime.now()
            target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0)

            if target <= now:
                target += timedelta(days=1)

            wait_seconds = (target - now).total_seconds()
            wait_minutes = int(wait_seconds / 60)

            print(f"⏰ Публикация запланирована на {args.time} (через {wait_minutes} мин.)")
            print("Не закрывай окно терминала!")

            import time
            time.sleep(wait_seconds)
            asyncio.run(send_to_telegram(post_text, bot_token, channel_id))
        except ValueError:
            print(f"\n❌ Неверный формат времени. Используй ЧЧ:ММ, например: 10:30\n")
            sys.exit(1)


if __name__ == "__main__":
    main()
