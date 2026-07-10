"""
НейроПост v2.0 — Главное меню
"""
import os
import sys
import subprocess


PASSPORT_FILE = "brand_passport.json"


def check_passport():
    return os.path.exists(PASSPORT_FILE)


def show_menu():
    passport_status = "✅ Паспорт Бренда создан" if check_passport() else "⚠️  Паспорт Бренда не создан (запусти setup.py)"
    print("\n" + "─" * 50)
    print("   НейроПост v2.0")
    print("─" * 50)
    print(f"   {passport_status}")
    print("─" * 50)
    print("  1. Написать пост")
    print("  2. Создать контент-план на 2 недели")
    print("  3. Опубликовать пост в Telegram")
    print("  4. Опубликовать пост в VK")
    print("  5. Сделать НейроАудит клиента (базовый)")
    print("  6. Сделать НейроАудит клиента (глубокий) [скоро]")
    print("  7. Создать скрипт продаж для клиента [скоро]")
    print("  0. Выход")
    print("─" * 50)


def run_module(script):
    try:
        subprocess.run([sys.executable, script], check=False)
    except FileNotFoundError:
        print(f"\n❌ Файл {script} не найден\n")
    except KeyboardInterrupt:
        print("\n\nОтменено. Возвращаемся в меню...\n")


def handle_publish_tg():
    print("\n" + "─" * 50)
    print("   Публикация в Telegram")
    print("─" * 50)

    posts_dir = "output/posts"
    if not os.path.exists(posts_dir):
        print("\n❌ Папка output/posts пуста. Сначала создай пост (пункт 1).\n")
        return

    files = [f for f in os.listdir(posts_dir) if f.endswith(".txt") and "TG" in f]
    if not files:
        print("\n❌ Нет файлов для Telegram (нужны файлы с _TG в названии).\n")
        return

    files.sort(reverse=True)
    print("\nДоступные файлы:")
    for i, f in enumerate(files[:10], start=1):
        print(f"  {i}. {f}")

    try:
        choice = int(input("\nВыбери номер файла: ").strip())
        if not 1 <= choice <= len(files):
            raise ValueError
        filepath = os.path.join(posts_dir, files[choice - 1])
    except (ValueError, IndexError):
        print("❌ Неверный выбор")
        return

    print("\n1. Опубликовать сейчас")
    print("2. Запланировать на время")
    time_choice = input("Выбери (1/2): ").strip()

    if time_choice == "1":
        subprocess.run([sys.executable, "publisher_tg.py", "--file", filepath, "--now"], check=False)
    elif time_choice == "2":
        pub_time = input("Время публикации (ЧЧ:ММ): ").strip()
        subprocess.run([sys.executable, "publisher_tg.py", "--file", filepath, "--time", pub_time], check=False)
    else:
        print("❌ Неверный выбор")


def handle_publish_vk():
    print("\n" + "─" * 50)
    print("   Публикация в VK")
    print("─" * 50)

    posts_dir = "output/posts"
    if not os.path.exists(posts_dir):
        print("\n❌ Папка output/posts пуста. Сначала создай пост (пункт 1).\n")
        return

    files = [f for f in os.listdir(posts_dir) if f.endswith(".txt") and "VK" in f]
    if not files:
        print("\n❌ Нет файлов для VK (нужны файлы с _VK в названии).\n")
        return

    files.sort(reverse=True)
    print("\nДоступные файлы:")
    for i, f in enumerate(files[:10], start=1):
        print(f"  {i}. {f}")

    try:
        choice = int(input("\nВыбери номер файла: ").strip())
        if not 1 <= choice <= len(files):
            raise ValueError
        filepath = os.path.join(posts_dir, files[choice - 1])
    except (ValueError, IndexError):
        print("❌ Неверный выбор")
        return

    print("\n1. Опубликовать сейчас")
    print("2. Запланировать на время")
    time_choice = input("Выбери (1/2): ").strip()

    if time_choice == "1":
        subprocess.run([sys.executable, "publisher_vk.py", "--file", filepath, "--now"], check=False)
    elif time_choice == "2":
        pub_time = input("Время публикации (ЧЧ:ММ): ").strip()
        subprocess.run([sys.executable, "publisher_vk.py", "--file", filepath, "--time", pub_time], check=False)
    else:
        print("❌ Неверный выбор")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not check_passport():
        print("\n" + "─" * 50)
        print("   НейроПост v2.0 — Добро пожаловать!")
        print("─" * 50)
        print("\nПаспорт Бренда не создан.")
        print("Без него генератор постов будет писать безликий текст.\n")
        choice = input("Создать Паспорт Бренда сейчас? (да/нет): ").strip().lower()
        if choice in ("да", "д", "yes", "y"):
            run_module("setup.py")

    while True:
        show_menu()
        choice = input("\nТвой выбор: ").strip()

        if choice == "1":
            if not check_passport():
                print("\n⚠️  Сначала создай Паспорт Бренда (запусти python setup.py)\n")
            else:
                run_module("generator.py")

        elif choice == "2":
            if not check_passport():
                print("\n⚠️  Сначала создай Паспорт Бренда (запусти python setup.py)\n")
            else:
                run_module("calendar_gen.py")

        elif choice == "3":
            handle_publish_tg()

        elif choice == "4":
            handle_publish_vk()

        elif choice == "5":
            if not check_passport():
                print("\n⚠️  Сначала создай Паспорт Бренда (запусти python setup.py)\n")
            else:
                run_module("audit_generator.py")

        elif choice == "6":
            print("\n🔧 Этот модуль в разработке. Скоро!\n")
            print("   НейроАудит глубокий (25 000 – 45 000 ₽) — Фаза 2.")
            input("\nНажми Enter для продолжения...")

        elif choice == "7":
            print("\n🔧 Этот модуль в разработке. Скоро!\n")
            print("   Скрипты продаж (8 000 – 15 000 ₽) — строится после Модулей 1, 3, 5.")
            input("\nНажми Enter для продолжения...")

        elif choice == "0":
            print("\nДо встречи! Работай умно. 🚀\n")
            sys.exit(0)

        else:
            print("\n❌ Неверный выбор. Введи цифру от 0 до 7.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nДо встречи!\n")
        sys.exit(0)
