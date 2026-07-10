"""
НейроПост v2.0 — Модуль 0: Создание Паспорта Бренда
"""
import json
import os
import sys

PASSPORT_FILE = "brand_passport.json"

QUESTIONS = [
    ("who_i_am", "Кто ты и чем занимаешься? (1-2 предложения, как объяснила бы подруге)"),
    ("target_client", "Кому помогаешь? (опиши клиента: кто он, какая у него боль)"),
    ("main_result", "Какой главный результат получает клиент от работы с тобой?"),
    ("differentiation", "Чем ты отличаешься от других? (честно, без «индивидуального подхода»)"),
    ("tone", "Как ты говоришь? (выбери или опиши: строго / тепло / с юмором / по-деловому / как подруга)"),
    ("my_phrases", "Напиши 3 фразы, которые ты реально используешь в жизни (через запятую)"),
    ("never_say", "Что ты НИКОГДА не скажешь клиенту? (через запятую)"),
    ("offer", "Твой оффер одним предложением (что + для кого + результат)"),
    ("archetypes", "Твои архетипы (например: Герой, Правитель, Маг — через запятую)"),
    ("price_base", "Цена базовой услуги (только число в рублях, например: 12000)"),
]


def ask_question(number, total, question):
    print(f"\nВопрос {number}/{total}: {question}")
    answer = input("Твой ответ: ").strip()
    while not answer:
        print("Ответ не может быть пустым. Попробуй снова.")
        answer = input("Твой ответ: ").strip()
    return answer


def main():
    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — Паспорт Бренда")
    print("─" * 50)
    print("\nПривет! Давай создадим твой Паспорт Бренда.")
    print("Это займёт 5-7 минут и нужно сделать один раз.\n")

    if os.path.exists(PASSPORT_FILE):
        print("⚠️  Паспорт Бренда уже существует.")
        choice = input("Обновить его? (да/нет): ").strip().lower()
        if choice not in ("да", "д", "yes", "y"):
            print("\nОставляем старый паспорт. Для запуска приложения: python main.py")
            sys.exit(0)
        print("\nОбновляем паспорт...\n")

    passport = {}
    total = len(QUESTIONS)

    for i, (key, question) in enumerate(QUESTIONS, start=1):
        answer = ask_question(i, total, question)

        if key == "my_phrases":
            passport[key] = [p.strip() for p in answer.split(",") if p.strip()]
        elif key == "never_say":
            passport[key] = [p.strip() for p in answer.split(",") if p.strip()]
        elif key == "archetypes":
            passport[key] = [p.strip() for p in answer.split(",") if p.strip()]
        elif key == "price_base":
            try:
                passport[key] = int(answer.replace(" ", "").replace("₽", ""))
            except ValueError:
                passport[key] = answer
        else:
            passport[key] = answer

    with open(PASSPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(passport, f, ensure_ascii=False, indent=2)

    print("\n" + "─" * 50)
    print("✅  Паспорт создан!")
    print("─" * 50)
    print("\nТеперь запусти: python main.py\n")


if __name__ == "__main__":
    main()
