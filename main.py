"""
НейроПост v2.0 — Главное меню с выбором профиля
"""
import json
import os
import sys
import subprocess

PROFILES_DIR = "profiles"
OWNER_FILE = os.path.join(PROFILES_DIR, "owner.json")


def load_json(filepath):
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def get_all_profiles():
    """Возвращает [(filename, data), ...] — сначала owner, потом клиенты по алфавиту"""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    files = sorted(f for f in os.listdir(PROFILES_DIR) if f.endswith(".json"))
    profiles = []
    for fname in files:
        try:
            data = load_json(os.path.join(PROFILES_DIR, fname))
            profiles.append((fname, data))
        except Exception:
            pass
    # Owner первым
    profiles.sort(key=lambda x: 0 if x[1].get("_type") == "owner" else 1)
    return profiles


def select_profile():
    """Показывает список профилей и возвращает выбранный (filename, data)"""
    profiles = get_all_profiles()

    if not profiles:
        return None, None

    print("\n" + "─" * 50)
    print("   Выбери профиль")
    print("─" * 50)

    for i, (fname, data) in enumerate(profiles, 1):
        if data.get("_type") == "owner":
            label = "👤 Я сама (мой личный бренд)"
        else:
            name = data.get("name") or data.get("who_i_am", fname)[:35]
            niche = data.get("who_i_am", "")[:40]
            label = f"🏢 {name} — {niche}"
        print(f"  {i}. {label}")

    print()
    try:
        choice = int(input("Номер профиля: ").strip())
        if 1 <= choice <= len(profiles):
            return profiles[choice - 1]
    except ValueError:
        pass

    print("❌ Неверный выбор")
    return None, None


def run_module(script, extra_args=None):
    cmd = [sys.executable, script]
    if extra_args:
        cmd += extra_args
    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print(f"\n❌ Файл {script} не найден\n")
    except KeyboardInterrupt:
        print("\n\nОтменено. Возвращаемся в меню...\n")


def show_menu(profile_name):
    print("\n" + "─" * 50)
    print(f"   НейроПост v2.0  |  {profile_name}")
    print("─" * 50)
    print("  1. Написать пост")
    print("  2. Создать контент-план на 2 недели")
    print("  3. Опубликовать пост в Telegram")
    print("  4. Опубликовать пост в VK")
    print("  5. Сделать НейроАудит клиента (базовый)")
    print("  6. Сделать НейроАудит клиента (глубокий) [скоро]")
    print("  7. Создать скрипт продаж для клиента [скоро]")
    print("  ─")
    print("  8. Управление профилями (добавить клиента)")
    print("  9. Сменить профиль")
    print("  0. Выход")
    print("─" * 50)


def get_post_files(platform_filter=None):
    posts_dir = "output/posts"
    if not os.path.exists(posts_dir):
        return []
    files = [f for f in os.listdir(posts_dir) if f.endswith(".txt")]
    if platform_filter:
        files = [f for f in files if platform_filter in f]
    return sorted(files, reverse=True)


def pick_post_file(platform):
    files = get_post_files(platform)
    if not files:
        print(f"\n❌ Нет файлов для {platform}. Сначала создай пост (пункт 1).\n")
        return None

    print(f"\nДоступные посты для {platform}:")
    for i, f in enumerate(files[:10], 1):
        print(f"  {i}. {f}")

    try:
        choice = int(input("\nНомер файла: ").strip())
        if 1 <= choice <= len(files):
            return os.path.join("output/posts", files[choice - 1])
    except ValueError:
        pass
    print("❌ Неверный выбор")
    return None


def handle_publish(platform, script):
    filepath = pick_post_file(platform)
    if not filepath:
        return
    print("\n1. Опубликовать сейчас")
    print("2. Запланировать на время")
    choice = input("Выбор (1/2): ").strip()
    if choice == "1":
        run_module(script, ["--file", filepath, "--now"])
    elif choice == "2":
        t = input("Время (ЧЧ:ММ): ").strip()
        run_module(script, ["--file", filepath, "--time", t])


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Первый запуск — нет профиля владельца
    if not os.path.exists(OWNER_FILE):
        print("\n" + "─" * 50)
        print("   НейроПост v2.0 — Добро пожаловать!")
        print("─" * 50)
        print("\nДля начала создадим твой личный профиль эксперта.")
        print("Это займёт 5 минут и делается один раз.\n")
        input("Нажми Enter чтобы начать...")
        run_module("setup.py")

    # Выбор профиля
    active_file, active_data = select_profile()

    if not active_data:
        print("\n❌ Профили не найдены. Запусти setup.py сначала.\n")
        sys.exit(1)

    is_owner = active_data.get("_type") == "owner"
    profile_label = "Я сама" if is_owner else active_data.get("name", "Клиент")

    while True:
        show_menu(profile_label)
        choice = input("\nТвой выбор: ").strip()

        profile_path = os.path.join(PROFILES_DIR,
                                    "owner.json" if is_owner else active_file)

        if choice == "1":
            run_module("generator.py", ["--profile", profile_path])

        elif choice == "2":
            run_module("calendar_gen.py", ["--profile", profile_path])

        elif choice == "3":
            handle_publish("TG", "publisher_tg.py")

        elif choice == "4":
            handle_publish("VK", "publisher_vk.py")

        elif choice == "5":
            # Аудит: owner = эксперт, active = клиент (или сам себя если owner)
            owner_path = OWNER_FILE
            client_path = profile_path
            run_module("audit_generator.py", [
                "--owner", owner_path,
                "--client", client_path,
            ])

        elif choice in ("6", "7"):
            print("\n🔧 Этот модуль в разработке. Скоро!\n")
            input("Enter для продолжения...")

        elif choice == "8":
            run_module("setup.py")

        elif choice == "9":
            active_file, active_data = select_profile()
            if active_data:
                is_owner = active_data.get("_type") == "owner"
                profile_label = "Я сама" if is_owner else active_data.get("name", "Клиент")

        elif choice == "0":
            print("\nДо встречи! 🚀\n")
            sys.exit(0)

        else:
            print("\n❌ Введи цифру от 0 до 9\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nДо встречи!\n")
