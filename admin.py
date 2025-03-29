import os
import telebot #бот кстати сделал @worpli а его даже никто не отблагодарил
from fpdf import FPDF
import database
from datetime import datetime

ADMIN_ID = здесь id админа для получения pdf с данными
FONT_PATH = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")

def safe_text(text):
    if text is None:
        return ""
    text = str(text)
    try:
        return text.encode('utf-8').decode('utf-8')
    except UnicodeError:
        try:
            return text.encode('cp1251', errors='replace').decode('cp1251')
        except:
            return text.encode('ascii', errors='replace').decode('ascii')

def generate_pdf_report():
    summary = database.get_summary()
    donations = database.get_donations()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    try:
        pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
        pdf.set_font("DejaVu", "", 16)
    except:
        try:
            pdf.add_font("Arial", "", "arial.ttf", uni=True)
            pdf.set_font("Arial", "", 16)
        except:
            pdf.set_font("Arial", "", 16)
    pdf.cell(0, 10, "Отчёт по донатам", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font_size(12)
    pdf.cell(0, 10, f"Общее количество донатов: {summary['total']} ₽", ln=True)
    pdf.cell(0, 10, f"За месяц: {summary['month']} ₽", ln=True)
    pdf.cell(0, 10, f"За сегодня: {summary['today']} ₽", ln=True)
    top_donor = summary['top_donor']
    top_name = safe_text(top_donor['full_name']) or "Не указано"
    raw_top_username = safe_text(top_donor['username'])
    if raw_top_username and not raw_top_username.startswith("@"):
        top_username = f"@{raw_top_username}"
    else:
        top_username = raw_top_username if raw_top_username else "—"
    pdf.cell(0, 10, f"Топ донатер: {top_name} ({top_username}) - {top_donor['amount']} ₽", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Cryptobot: {summary['sum_methods'].get('Cryptobot', 0)} ₽", ln=True)
    pdf.cell(0, 10, f"YooMoney: {summary['sum_methods'].get('YooMoney', 0)} ₽", ln=True)
    pdf.cell(0, 10, f"Stars: {summary['sum_methods'].get('Stars', 0)} ₽", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, f"Самый популярный метод: {summary['most_used']}", ln=True)
    pdf.ln(10)
    pdf.set_font_size(14)
    pdf.cell(0, 10, "Детальная история донатов:", ln=True)
    pdf.ln(5)
    pdf.set_font_size(10)
    column_widths = [40, 35, 25, 25, 40]
    headers = ["Имя", "Username", "Сумма", "Метод", "Дата и время"]
    for i, header in enumerate(headers):
        pdf.cell(column_widths[i], 10, header, border=1, align='C')
    pdf.ln()
    for donation in donations:
        if len(donation) < 5:
            continue  
        full_name, username, amount, method, donation_time = donation
        full_name = safe_text(full_name)
        if not full_name or full_name.strip() in ("—", "-", ""):
            full_name = "Не указано"
        username = safe_text(username)
        if username and username != "None":
            username = username if username.startswith("@") else f"@{username}"
        else:
            username = "—"
        try:
            dt_str = str(donation_time).split('.')[0]
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            formatted_time = dt.strftime("%d.%m.%Y %H:%M")
        except:
            formatted_time = dt_str[:16]
        pdf.cell(column_widths[0], 8, full_name, border=1)
        pdf.cell(column_widths[1], 8, username, border=1)
        pdf.cell(column_widths[2], 8, f"{amount} ₽", border=1, align='R')
        pdf.cell(column_widths[3], 8, method, border=1)
        pdf.cell(column_widths[4], 8, formatted_time, border=1)
        pdf.ln()
    file_name = "report.pdf"
    pdf.output(file_name)
    return file_name

def register_admin_handler(bot: telebot.TeleBot):
    @bot.message_handler(commands=["admin"])
    def admin_command(message):
        if message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "У вас нет доступа к этой команде.")
            return
        try:
            pdf_file = generate_pdf_report()
            with open(pdf_file, "rb") as file:
                bot.send_document(
                    message.chat.id, 
                    file, 
                    caption="📄 Отчёт по донатам",
                    parse_mode="Markdown"
                )
            os.remove(pdf_file)
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка генерации отчета: {str(e)}")