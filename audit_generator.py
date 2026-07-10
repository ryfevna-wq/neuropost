"""
НейроПост v2.0 — Модуль 5: Генератор НейроАудита (Режим А — базовый)
"""
import json
import os
import sys
from datetime import date
from dotenv import load_dotenv
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

load_dotenv()

PASSPORT_FILE = "brand_passport.json"
OUTPUT_DIR = "output/audits"
PROMPT_FILE = "prompts/audit_base.txt"


def load_passport():
    if not os.path.exists(PASSPORT_FILE):
        print("\n❌ Паспорт Бренда не найден. Сначала запусти: python setup.py\n")
        sys.exit(1)
    with open(PASSPORT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_audit_prompt():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def build_audit_system_prompt(passport):
    base_prompt = load_audit_prompt()

    if base_prompt:
        return base_prompt

    return """Ты — ИИ-Стратег, эксперт по маркетингу и продажам для малого бизнеса.
Твоя задача — провести глубокий аудит бизнеса клиента и найти ключевые точки роста.

Структура твоего аудита:
1. РЕНТГЕН БИЗНЕСА — анализ текущей ситуации, выявление 3 главных дыр
2. ДОРОЖНАЯ КАРТА — 4-шаговый план устранения дыр (конкретные действия)
3. СКРИПТ ЗАКРЫТИЯ — как эксперту предложить свои услуги после аудита

Будь конкретным, честным, без воды. Каждая дыра — с объяснением почему это проблема
и какие деньги/клиентов это стоит. Каждый шаг дорожной карты — конкретное действие."""


def run_audit(client_name, niche, site_text, audience, passport):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ GEMINI_API_KEY не найден в .env файле\n")
        sys.exit(1)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    audience_line = f"\nЦелевая аудитория: {audience}" if audience else ""

    prompt = f"""{build_audit_system_prompt(passport)}

Проведи НейроАудит этого бизнеса:

Имя/название: {client_name}
Ниша: {niche}{audience_line}

Текст сайта или оффера:
{site_text}

Напиши аудит строго в трёх разделах:

## РЕНТГЕН БИЗНЕСА
[Анализ и 3 ключевые дыры с объяснением потерь]

## ДОРОЖНАЯ КАРТА
[4 конкретных шага с действиями и сроками]

## СКРИПТ ЗАКРЫТИЯ
[Как предложить помощь клиенту после аудита — конкретные фразы]"""

    print("\n⏳ Анализирую бизнес клиента...")

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"\n❌ Ошибка при генерации аудита: {e}\n")
        sys.exit(1)


def create_word_report(audit_text, client_name, niche):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = date.today().strftime("%Y-%m-%d")
    safe_name = client_name.replace(" ", "_").replace("/", "-")
    filename = f"НейроАудит_{safe_name}_{today}.docx"
    filepath = os.path.join(OUTPUT_DIR, filename)

    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)

    title = doc.add_heading("НейроАудит", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)

    subtitle = doc.add_paragraph(f"{client_name} • {niche} • {today}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = Pt(12)
    subtitle.runs[0].font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)

    doc.add_paragraph()

    sections = audit_text.split("##")
    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n", 1)
        section_title = lines[0].strip()
        section_body = lines[1].strip() if len(lines) > 1 else ""

        if section_title:
            heading = doc.add_heading(section_title, level=1)
            heading.runs[0].font.color.rgb = RGBColor(0x27, 0xAE, 0x60)

        if section_body:
            for paragraph in section_body.split("\n\n"):
                paragraph = paragraph.strip()
                if paragraph:
                    p = doc.add_paragraph(paragraph)
                    p.paragraph_format.space_after = Pt(6)

        doc.add_paragraph()

    footer = doc.add_paragraph("Создано с помощью НейроПост v2.0")
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.color.rgb = RGBColor(0xBD, 0xC3, 0xC7)

    doc.save(filepath)
    return filepath


def main():
    print("\n" + "─" * 50)
    print("   НейроПост v2.0 — НейроАудит клиента")
    print("─" * 50)
    print("\nРежим А — Базовый аудит (3 дыры + дорожная карта + скрипт закрытия)\n")

    passport = load_passport()

    client_name = input("Имя/название бизнеса клиента: ").strip()
    if not client_name:
        print("❌ Имя клиента обязательно")
        sys.exit(1)

    niche = input("Ниша клиента: ").strip()
    if not niche:
        print("❌ Ниша обязательна")
        sys.exit(1)

    print("\nВставь текст сайта или оффера клиента.")
    print("Когда закончишь — введи пустую строку и нажми Enter дважды:")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    site_text = "\n".join(lines).strip()

    if not site_text:
        print("❌ Текст сайта/оффера обязателен")
        sys.exit(1)

    audience = input("\nЦелевая аудитория (опционально, Enter — пропустить): ").strip()

    audit_text = run_audit(client_name, niche, site_text, audience, passport)

    filepath = create_word_report(audit_text, client_name, niche)

    print("\n" + "─" * 50)
    print("✅ НейроАудит готов!")
    print(f"📄 Файл: {filepath}")
    print("─" * 50)
    print("\nПредпросмотр:\n")
    print(audit_text[:500] + "..." if len(audit_text) > 500 else audit_text)
    print()


if __name__ == "__main__":
    main()
