"""
НейроПост v2.0 — Модуль 0: Управление профилями
"""
import json
import os
import sys

PROFILES_DIR = "profiles"
OWNER_FILE = os.path.join(PROFILES_DIR, "owner.json")

QUESTIONS_OWNER = [
    ("who_i_am",        "Кто ты и чем занимаешься? (1-2 предложения, как объяснила бы подруге)"),
    ("target_client",   "Кому помогаешь? (опиши клиента: кто он, какая у него боль)"),
    ("main_result",     "Какой главный результат получает клиент от работы с тобой?"),
    ("differentiation", "Чем ты отличаешься от других? (честно, без «индивидуального подхода»)"),
    ("tone",            "Как ты говоришь? (строго / тепло / с юмором / по-деловому / как подруга)"),
    ("my_phrases",      "Напиши 3 фразы, которые ты реально используешь в жизни (через запятую)"),
    ("never_say",       "Что ты НИКОГДА не скажешь клиенту? (через запятую)"),
    ("offer",           "Твой оффер одним предложением (что + для кого + результат)"),
    ("archetypes",      "Твои архетипы (например: Герой, Правитель, Маг — через запятую)"),
    ("price_base",      "Цена твоей базовой услуги (только число, например: 12000)"),
]

QUESTIONS_CLIENT = [
    ("name",            "Имя или название бизнеса клиента"),
    ("who_i_am",        "Чем занимается клиент? (1-2 предложения)"),
    ("target_client",   "Кому продаёт? (его целевая аудитория и их боль)"),
    ("main_result",     "Какой главный результат даёт клиент своим покупателям?"),
    ("differentiation", "В чём уникальность клиента? (его отличие от конкурентов)"),
    ("tone",            "В каком стиле общается клиент? (строго / тепло / с юмором / по-деловому)"),
    ("my_phrases",      "3 характерные фразы клиента (через запятую) — или придумай по стилю"),
    ("never_say",       "Что клиент НИКОГДА не скажет своей аудитории? (через запятую)"),
    ("offer",           "Оффер клиента одним предложением (что + для кого + результат)"),
    ("price_base",      "Цена основной услуги клиента (только число)"),
]


def parse_answer(key, answer):
    if key in ("my_phrases", "never_say", "archetypes"):
        return [p.strip() for p in answer.split(",") if p.strip()]
    if key == "price_base":
        try:
            return int(answer.replace(" ", "").replace("₽", ""))
        except ValueError:
            return answer
    return answer


def ask_questions(questions):
    data = {}
    total = len(questions)
    for i, (key, question) in enumerate(questions, 1):
        print(f"\nВопрос {i}/{total}: {question}")
        answer = input("Ответ: ").strip()
        while not answer:
            print("Нельзя оставить пустым. Попробуй снова.")
            answer = input("Ответ: ").strip()
        data[key] = parse_answer(key, answer)
    return data


def save_profile(data, filepath):
    os.makedirs(PROFILES_DIR, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def name_to_filename(name):
    safe = name.lower().replace(" ", "_")
    keep = "abcdefghijklmnopqrstuvwxyz0123456789_абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    safe = "".join(c for c in safe if c in keep)
    return os.path.join(PROFILES_DIR, f"{safe}.json")


def create_owner():
    print("\n" + "─" * 50)
    print("   Создаём твой профиль (Эксперт)")
    print("─" * 50)
    print("\nЭто твой личный профиль — он будет подписывать")
    print("все НейроАудиты и использоваться для твоих постов.\n")

    data = ask_questions(QUESTIONS_OWNER)
    data["_type"] = "owner"

    save_profile(data, OWNER_FILE)
    print("\n✅ Твой профиль сохранён!\n")


def create_client():
    print("\n" + "─" * 50)
    print("   Создаём профиль клиента")
    print("─" * 50)
    print()

    data = ask_questions(QUESTIONS_CLIENT)
    data["_type"] = "client"

    filepath = name_to_filename(data.get("name", "client"))

    # Если файл уже есть — добавляем суффикс
    base = filepath.replace(".json", "")
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}.json"
        counter += 1

    save_profile(data, filepath)
    print(f"\n✅ Профиль клиента «{data.get('name')}» сохранён!\n")


def list_profiles():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    files = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    profiles = []
    for f in files:
        with open(os.path.join(PROFILES_DIR, f), encoding="utf-8") as fp:
            try:
                data = json.load(fp)
                profiles.append((f, data))
            except Exception:
                pass
    return profiles


def main():
    os.makedirs(PROFILES_DIR, exist_ok=True)

    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — Управление профилями")
    print("─" * 50)

    # Если нет профиля владельца — сначала создать его
    if not os.path.exists(OWNER_FILE):
        print("\n⚠️  Твой профиль (Эксперт) ещё не создан.")
        print("Это нужно сделать один раз — он будет подписывать все аудиты.\n")
        input("Нажми Enter чтобы начать...")
        create_owner()

    while True:
        print("\nЧто хочешь сделать?")
        print("  1. Добавить нового клиента")
        print("  2. Посмотреть все профили")
        print("  3. Обновить мой профиль (Эксперт)")
        print("  0. Выход в главное меню")
        choice = input("\nВыбор: ").strip()

        if choice == "1":
            create_client()

        elif choice == "2":
            profiles = list_profiles()
            print(f"\n{'─'*50}")
            for fname, data in profiles:
                ptype = "👤 Эксперт (ты)" if data.get("_type") == "owner" else "🏢 Клиент"
                name = data.get("name") or data.get("who_i_am", "")[:40]
                print(f"  {ptype}: {name}  [{fname}]")
            print(f"{'─'*50}")
            input("\nEnter для продолжения...")

        elif choice == "3":
            print("\n⚠️  Текущий профиль будет перезаписан.")
            confirm = input("Продолжить? (да/нет): ").strip().lower()
            if confirm in ("да", "д"):
                create_owner()

        elif choice == "0":
            print("\nВозвращаемся в главное меню...")
            sys.exit(0)

        else:
            print("❌ Неверный выбор")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nОтмена.\n")
