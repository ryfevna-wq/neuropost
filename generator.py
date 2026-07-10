"""
НейроПост v2.0 — Модуль 1: Генератор постов
"""
import json
import os
import sys
from datetime import date
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

PASSPORT_FILE = "brand_passport.json"
OUTPUT_DIR = "output/posts"

POST_TYPES = {
    "1": "полезный",
    "2": "история",
    "3": "кейс",
    "4": "анонс",
}

PLATFORMS = {
    "1": "TG",
    "2": "VK",
    "3": "MAX",
    "4": "все",
}

PLATFORM_INSTRUCTIONS = {
    "TG": "Формат для Telegram: до 4096 символов, можно эмодзи, без хэштегов в тексте (они в конце опционально), абзацы через пустую строку.",
    "VK": "Формат для ВКонтакте: до 15000 символов, добавь в конце 5-7 релевантных хэштегов через #, абзацы через пустую строку.",
    "MAX": "Формат для MAX (бывший Одноклассники): до 8000 символов, дружелюбный тон, эмодзи умеренно, абзацы через пустую строку.",
}


def load_passport():
    if not os.path.exists(PASSPORT_FILE):
        print("\n❌ Паспорт Бренда не найден. Сначала запусти: python setup.py\n")
        sys.exit(1)
    with open(PASSPORT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(passport):
    phrases = ", ".join(passport.get("my_phrases", []))
    never_say = ", ".join(passport.get("never_say", []))
    archetypes = ", ".join(passport.get("archetypes", []))

    return f"""Ты — контент-менеджер и копирайтер эксперта со следующим Паспортом Бренда:

КТО Я: {passport.get('who_i_am', '')}
МОЙ КЛИЕНТ: {passport.get('target_client', '')}
ГЛАВНЫЙ РЕЗУЛЬТАТ: {passport.get('main_result', '')}
МОЁ ОТЛИЧИЕ: {passport.get('differentiation', '')}
МОЙ ТОН: {passport.get('tone', '')}
МОИ ФРАЗЫ (использовать): {phrases}
НИКОГДА НЕ ГОВОРЮ: {never_say}
МОЙ ОФФЕР: {passport.get('offer', '')}
МОИ АРХЕТИПЫ: {archetypes}

Пиши посты от первого лица, в голосе и стиле эксперта.
Используй характерные фразы. Никогда не используй запрещённые слова и обороты.
Пиши живо, без канцелярита, как реальный человек."""


def build_user_prompt(topic, post_type, platform):
    platform_instruction = PLATFORM_INSTRUCTIONS.get(platform, PLATFORM_INSTRUCTIONS["TG"])

    type_instructions = {
        "полезный": "Напиши полезный пост: дай конкретную пользу читателю, используй структуру (проблема → суть → 3-5 советов → вывод). Заголовок — цепляющий.",
        "история": "Напиши пост-историю (сторителлинг): начни с яркого момента, покажи трансформацию, заверши выводом или призывом.",
        "кейс": "Напиши пост-кейс: ситуация клиента до → что сделали → результат в цифрах или конкретике → вывод для читателя.",
        "анонс": "Напиши пост-анонс: заинтригуй, объясни ценность, добавь чёткий призыв к действию.",
    }

    return f"""Тема поста: {topic}
Тип поста: {post_type}
{type_instructions.get(post_type, '')}

{platform_instruction}

После текста поста на отдельной строке напиши:
ПРОМПТ ДЛЯ ВИЗУАЛА: [короткое описание изображения для нейросети Кандинский/Шедеврум на русском языке]"""


def generate_post(topic, post_type, platform, passport):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY не найден в .env файле\n")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    platforms_to_generate = list(PLATFORM_INSTRUCTIONS.keys()) if platform == "все" else [platform]
    results = {}

    for p in platforms_to_generate:
        print(f"\n⏳ Генерирую пост для {p}...")
        try:
            prompt = build_system_prompt(passport) + "\n\n" + build_user_prompt(topic, post_type, p)
            response = model.generate_content(prompt)
            results[p] = response.text
        except Exception as e:
            print(f"\n❌ Ошибка при генерации для {p}: {e}\n")
            results[p] = None

    return results


def save_posts(results, topic):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    saved_files = []

    for platform, text in results.items():
        if text is None:
            continue
        filename = f"{today}_{platform}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        full_content = f"Тема: {topic}\nДата: {today}\nПлатформа: {platform}\n\n{'─'*50}\n\n{text}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        saved_files.append(filepath)

    return saved_files


def main():
    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — Генератор постов")
    print("─" * 50)

    passport = load_passport()

    topic = input("\nТема поста: ").strip()
    if not topic:
        print("❌ Тема не может быть пустой")
        sys.exit(1)

    print("\nТип поста:")
    for k, v in POST_TYPES.items():
        print(f"  {k}. {v}")
    type_choice = input("Выбери (1-4): ").strip()
    post_type = POST_TYPES.get(type_choice, "полезный")

    print("\nПлатформа:")
    for k, v in PLATFORMS.items():
        print(f"  {k}. {v}")
    platform_choice = input("Выбери (1-4): ").strip()
    platform = PLATFORMS.get(platform_choice, "TG")

    results = generate_post(topic, post_type, platform, passport)

    saved = save_posts(results, topic)

    print("\n" + "─" * 50)
    for platform_name, text in results.items():
        if text:
            print(f"\n✅ Пост для {platform_name}:\n")
            print(text)
            print()

    print("─" * 50)
    print("💾 Сохранено в файлы:")
    for f in saved:
        print(f"   {f}")
    print()


if __name__ == "__main__":
    main()
