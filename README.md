

### Telegram Donation Bot

Этот бот позволяет принимать донаты через три способа оплаты:

**Cryptobot** – оплата в криптовалюте.

**YooMoney** – оплата через YooMoney.

**Telegram Stars** – стандартный платёж через Telegram.


После успешной оплаты бот отправляет уведомление в указанный канал с информацией о донате, генерирует PDF‑отчёт и предоставляет ссылку на конкретное сообщение в канале, где отображается информация о пожертвовании.
### Внимание: Минимальная сумма доната в файле config должна быть более 10, иначе оплата Cryptobot не будет работать 

---

### 🚀 Возможности

Принимает сумму доната от пользователя с проверкой минимальной суммы (только суммы больше 10₽ допустимы).

Предоставляет выбор способа оплаты через inline‑клавиатуру.

Генерирует ссылку для оплаты через Cryptobot и YooMoney.

Обрабатывает успешные платежи через Telegram Stars.

Периодически проверяет статус платежей для Cryptobot и YooMoney.

После успешной оплаты редактирует сообщение пользователя, добавляя кнопку со ссылкой на сообщение в канале.

Генерирует PDF‑отчёт с подробной статистикой донатов, где отдельно отображаются имя и username донатёра.

Команда /admin позволяет получить PDF‑отчёт по донатам (для её использования необходимо указать свой ID в файле admin.py).




---

### 🛠 Установка

1. Скачайте релиз

Вместо клонирования репозитория можно загрузить готовую версию бота из релизов.

2. Установите необходимые библиотеки

Для работы бота потребуются следующие библиотеки:

**pyTelegramBotAPI**

**requests**

**yoomoney**

**fpdf**


Установите их с помощью команды:
```
pip install pyTelegramBotAPI requests yoomoney fpdf
```
Или, если имеется файл requirements.txt, выполните:
```
pip install -r requirements.txt
```
3. Настройка конфигурации

В файле config.py необходимо указать заполнители (замените их на реальные значения по мере необходимости):
```
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CRYPTOBOT_API_TOKEN = "YOUR_CRYPTOBOT_API_TOKEN"
YOOMONEY_TOKEN = "YOUR_YOOMONEY_TOKEN"
YOOMONEY_RECEIVER = "YOUR_YOOMONEY_RECEIVER"
TELEGRAM_PAYMENT_PROVIDER_TOKEN = "YOUR_TELEGRAM_PAYMENT_PROVIDER_TOKEN"
CHANNEL_LINK = "@yourchannel"
MIN_DONATION = 10  # Минимальная сумма доната (больше 10₽)
CONVERSION_API_URL = "https://api.exchangerate-api.com/v4/latest/RUB"
BOT_LINK = "https://t.me/your_bot"
```
4. Настройка команды /admin

В файле admin.py необходимо указать свой Telegram ID (переменная ADMIN_ID), чтобы иметь доступ к команде /admin, которая отправляет PDF‑отчёт со статистикой донатов.

5. Создание канала и настройка бота

Создайте канал в Telegram, который будет использоваться для отображения донатов.

Добавьте бота в канал и назначьте его администратором, чтобы он мог отправлять и редактировать сообщения.

Убедитесь, что бот имеет достаточные права для генерации PDF‑отчётов и отправки сообщений.


6. Запуск бота

После внесения всех настроек запустите бота командой:
```
python main.py
```
**Как получить токен от YooMoney -> 
---

### 📂 Структура проекта

**main.py** – основной файл, содержащий логику работы бота, обработку сообщений, платежей и периодическую проверку статусов платежей. Теперь данные доната разделены на два поля: full_name и username.

**publication.py** – модуль для отправки сообщений о донате в канал и редактирования сообщений пользователя с добавлением ссылки на конкретное сообщение.

**payment.py** – модуль для работы с платежными системами (Cryptobot и YooMoney), включает получение ссылки для оплаты и проверку статуса платежей.

**admin.py** – модуль для генерации PDF‑отчёта по донатам, где отображаются статистика, данные о топ‑донатёре и детальная история транзакций. Для доступа к команде /admin необходимо указать свой ID.

**database.py** – модуль для работы с SQLite‑базой данных, хранит информацию о донатах.

**config.py** – файл с настройками и ключами, необходимыми для работы бота.



---

### 📄 Примечания

Если в PDF‑отчёте некоторые символы отображаются в виде квадратиков, убедитесь, что выбранный шрифт (например, DejaVuSans.ttf) поддерживает нужные символы. При необходимости попробуйте использовать другой шрифт с расширенной поддержкой Unicode.

Проверьте, чтобы при формировании доната данные full_name и username передавались отдельно – это необходимо для корректного отображения в PDF‑отчёте и для различения имени пользователя от его username.



---

### 📄 Лицензия

MIT License. Подробности в файле LICENSE.
