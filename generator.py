"""
НейроПост v2.0 — Модуль 1: Генератор постов
"""
import argparse
import json
import os
import sys
from datetime import date
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

OUTPUT_DIR = "output/posts"

POST_TYPES = {"1": "полезный", "2": "история", "3": "кейс", "4": "анонс"}
PLATFORMS  = {"1": "TG", "2": "VK", "3": "MAX", "4": "все"}

PLATFORM_INSTRUCTIONS = {
    "TG":  "Формат Telegram: до 4096 символов, можно эмодзи, абзацы через пустую строку.",
    "VK":  "Формат ВКонтакте: до 15000 символов, добавь в конце 5-7 хэштегов через #.",
    "MAX": "Формат MAX: до 8000 символов, дружелюбный тон, эмодзи умеренно.",
}


def load_profile(path):
    if not os.path.exists(path):
        print(f"\n❌ Профиль не найден: {path}\n")
        print("Запусти python setup.py чтобы создать профиль.\n")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(profile):
    phrases   = ", ".join(profile.get("my_phrases", []))
    never_say = ", ".join(profile.get("never_say", []))
    archetypes = ", ".join(profile.get("archetypes", []))
    name = profile.get("name") or "эксперт"

    return f"""Ты — копирайтер эксперта. Пиши посты от первого лица в его голосе.

Паспорт Бренда:
ИМЯ/БРЕНД: {name}
КТО Я: {profile.get('who_i_am', '')}
МОЙ КЛИЕНТ: {profile.get('target_client', '')}
РЕЗУЛЬТАТ: {profile.get('main_result', '')}
ОТЛИЧИЕ: {profile.get('differentiation', '')}
ТОН: {profile.get('tone', '')}
МОИ ФРАЗЫ: {phrases}
НИКОГДА НЕ ГОВОРЮ: {never_say}
ОФФЕР: {profile.get('offer', '')}
АРХЕТИПЫ: {archetypes}

Используй характерные фразы. Никогда не используй запрещённые обороты.
Пиши живо, без канцелярита."""


def build_user_prompt(topic, post_type, platform):
    type_instructions = {
        "полезный": "Структура: цепляющий заголовок → проблема → 3-5 советов → вывод → мягкий призыв.",
        "история":  "Структура: яркое начало → развитие → кульминация → вывод/урок.",
        "кейс":     "Структура: ситуация ДО → что сделали → результат в цифрах → вывод.",
        "анонс":    "Структура: интрига → ценность → чёткий призыв к действию.",
    }
    return f"""Тема: {topic}
Тип: {post_type}
{type_instructions.get(post_type, '')}

{PLATFORM_INSTRUCTIONS.get(platform, '')}

После текста добавь строку:
ПРОМПТ ДЛЯ ВИЗУАЛА: [описание картинки для Кандинского/Шедеврума]"""


def generate_post(topic, post_type, platform, profile):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY не найден в .env файле\n")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    platforms_list = list(PLATFORM_INSTRUCTIONS.keys()) if platform == "все" else [platform]
    results = {}

    for p in platforms_list:
        print(f"\n⏳ Генерирую пост для {p}...")
        try:
            prompt = build_system_prompt(profile) + "\n\n" + build_user_prompt(topic, post_type, p)
            response = model.generate_content(prompt)
            results[p] = response.text
        except Exception as e:
            print(f"\n❌ Ошибка для {p}: {e}\n")
            results[p] = None

    return results


def save_posts(results, topic):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    saved = []
    for platform, text in results.items():
        if not text:
            continue
        filepath = os.path.join(OUTPUT_DIR, f"{today}_{platform}.txt")
        content = f"Тема: {topic}\nДата: {today}\nПлатформа: {platform}\n\n{'─'*50}\n\n{text}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        saved.append(filepath)
    return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profiles/owner.json")
    args = parser.parse_args()

    profile = load_profile(args.profile)
    brand_name = profile.get("name") or "мой бренд"

    print("\n" + "─" * 50)
    print(f"   Генератор постов  |  {brand_name}")
    print("─" * 50)

    topic = input("\nТема поста: ").strip()
    if not topic:
        print("❌ Тема не может быть пустой")
        sys.exit(1)

    print("\nТип поста:")
    for k, v in POST_TYPES.items():
        print(f"  {k}. {v}")
    post_type = POST_TYPES.get(input("Выбери (1-4): ").strip(), "полезный")

    print("\nПлатформа:")
    for k, v in PLATFORMS.items():
        print(f"  {k}. {v}")
    platform = PLATFORMS.get(input("Выбери (1-4): ").strip(), "TG")

    results = generate_post(topic, post_type, platform, profile)
    saved = save_posts(results, topic)

    print("\n" + "─" * 50)
    for p, text in results.items():
        if text:
            print(f"\n✅ Пост для {p}:\n\n{text}\n")
    print("─" * 50)
    print("💾 Сохранено:")
    for f in saved:
        print(f"   {f}")
    print()


if __name__ == "__main__":
    main()
