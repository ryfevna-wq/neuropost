"""
НейроПост v2.0 — Модуль 2: Генератор контент-плана
"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

load_dotenv()

OUTPUT_DIR = "output"
DAYS_RU = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def load_profile(path):
    if not os.path.exists(path):
        print(f"\n❌ Профиль не найден: {path}\n")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def generate_topics(profile, posts_per_week, weeks=2):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY не найден в .env файле\n")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    total = posts_per_week * weeks
    name  = profile.get("name") or "эксперт"

    prompt = f"""Ты — контент-стратег. Создай контент-план для эксперта.

Бренд: {name}
Ниша: {profile.get('who_i_am', '')}
Клиент эксперта: {profile.get('target_client', '')}
Тон: {profile.get('tone', '')}
Оффер: {profile.get('offer', '')}

Придумай {total} тем для постов на {weeks} недели.
Чередуй типы: полезный, история, кейс, анонс, вирусный, личное.

Ответь ТОЛЬКО списком (одна тема на строку), формат:
ТИП|ТЕМА|ХЭШТЕГИ

Пример:
полезный|5 ошибок при настройке таргета|#таргет #реклама #маркетинг #ошибки #бизнес
история|Как я потеряла клиента из-за одного слова|#история #опыт #продажи #урок

Дай ровно {total} строк, без нумерации, без лишнего текста."""

    print(f"\n⏳ Генерирую {total} тем...")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"\n❌ Ошибка: {e}\n")
        sys.exit(1)


def parse_topics(raw, total):
    topics = []
    for line in raw.split("\n"):
        line = line.strip()
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) >= 2:
                topics.append((
                    parts[0].strip(),
                    parts[1].strip(),
                    parts[2].strip() if len(parts) > 2 else "",
                ))
        if len(topics) >= total:
            break
    return topics


def create_excel(topics, start_date, posts_per_week, brand_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today    = date.today().strftime("%Y-%m-%d")
    filepath = os.path.join(OUTPUT_DIR, f"calendar_{today}.xlsx")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Контент-план"

    headers     = ["Дата", "День", "Тип поста", "Тема", "Хэштеги", "Статус"]
    header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
    header_font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )

    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.fill, cell.font = header_fill, header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    ws.row_dimensions[1].height = 25

    type_colors = {
        "полезный": "27AE60", "история": "8E44AD", "кейс": "2980B9",
        "анонс": "E74C3C", "вирусный": "F39C12", "личное": "16A085",
    }
    fill_even   = PatternFill(start_color="ECF0F1", end_color="ECF0F1", fill_type="solid")
    fill_odd    = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    status_fill = PatternFill(start_color="EBF5FB", end_color="EBF5FB", fill_type="solid")

    step     = max(1, 7 // posts_per_week)
    offsets  = [i * step for i in range(posts_per_week)]
    idx, row = 0, 2

    for week in range(2):
        week_start = start_date + timedelta(weeks=week)
        for offset in offsets:
            if idx >= len(topics):
                break
            post_date = week_start + timedelta(days=offset)
            ptype, theme, tags = topics[idx]
            fill = fill_even if row % 2 == 0 else fill_odd

            for col, val in enumerate(
                [post_date.strftime("%d.%m.%Y"), DAYS_RU[post_date.weekday()],
                 ptype, theme, tags, "📝 Не начат"], 1
            ):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = border
                cell.alignment = Alignment(vertical="center", wrap_text=True)
                cell.fill = status_fill if col == 6 else fill
                if col == 3:
                    color = next((v for k, v in type_colors.items() if k in ptype.lower()), "000000")
                    cell.font = Font(name="Arial", color=color, bold=True, size=10)
                else:
                    cell.font = Font(name="Arial", size=10)

            ws.row_dimensions[row].height = 45
            idx += 1
            row += 1

    for i, w in enumerate([14, 14, 18, 45, 35, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.insert_rows(1)
    ws.merge_cells("A1:F1")
    tc = ws["A1"]
    tc.value = f"{brand_name} | Контент-план на 2 недели | Старт: {start_date.strftime('%d.%m.%Y')}"
    tc.font      = Font(name="Arial", bold=True, size=13, color="2C3E50")
    tc.alignment = Alignment(horizontal="center", vertical="center")
    tc.fill      = PatternFill(start_color="D5E8D4", end_color="D5E8D4", fill_type="solid")
    ws.row_dimensions[1].height = 30

    wb.save(filepath)
    return filepath


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="profiles/owner.json")
    args = parser.parse_args()

    profile    = load_profile(args.profile)
    brand_name = profile.get("name") or "мой бренд"

    print("\n" + "─" * 50)
    print(f"   Контент-план  |  {brand_name}")
    print("─" * 50)

    try:
        ppw = int(input("\nСколько постов в неделю? (1-7): ").strip())
        if not 1 <= ppw <= 7:
            raise ValueError
    except ValueError:
        print("❌ Введи число от 1 до 7")
        sys.exit(1)

    start_input = input("Дата старта (ДД.ММ.ГГГГ, Enter = сегодня): ").strip()
    if start_input:
        try:
            from datetime import datetime
            start_date = datetime.strptime(start_input, "%d.%m.%Y").date()
        except ValueError:
            print("❌ Неверный формат даты")
            sys.exit(1)
    else:
        start_date = date.today()

    raw    = generate_topics(profile, ppw)
    topics = parse_topics(raw, ppw * 2)
    path   = create_excel(topics, start_date, ppw, brand_name)

    print("\n" + "─" * 50)
    print("✅ Контент-план готов!")
    print(f"📊 Файл: {path}")
    print(f"   {len(topics)} постов на 2 недели")
    print("─" * 50 + "\n")


if __name__ == "__main__":
    main()
