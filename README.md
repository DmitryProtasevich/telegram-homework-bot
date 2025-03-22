# homework_bot

### ОПИСАНИЕ
Бот-ассистент — это Telegram-бот, который помогает отслеживать статус домашних работ, отправленных на проверку в сервис "Практикум Домашка". Бот периодически опрашивает API сервиса и отправляет уведомления в Telegram при изменении статуса домашней работы. Проект разработан с использованием Python и библиотеки pyTelegramBotAPI.

Основная цель проекта — автоматизировать процесс отслеживания статуса домашних работ и уведомлять пользователя о важных изменениях.

Что делает бот:
Опрашивает API сервиса "Практикум Домашка" раз в 10 минут.
Проверяет статус домашней работы:
Работа взята в ревью.
Работа проверена (принята или возвращена на доработку).
Отправляет уведомления в Telegram при изменении статуса.
Логирует свою работу и сообщает о важных проблемах в Telegram.

### КЛЮЧЕВЫЕ ФУНКЦИИ
Основные функции:
check_tokens():
Проверяет доступность обязательных переменных окружения:
PRACTICUM_TOKEN — токен для доступа к API "Практикум Домашка".
TELEGRAM_TOKEN — токен для доступа к Telegram-боту.
TELEGRAM_CHAT_ID — ID чата для отправки уведомлений.
Если отсутствует хотя бы одна переменная, работа бота прекращается.

get_api_answer(timestamp):
Выполняет запрос к API сервиса "Практикум Домашка".
Возвращает ответ API, преобразованный из JSON в Python-объект.
Логирует параметры запроса и обрабатывает ошибки соединения.

check_response(response):
Проверяет ответ API на соответствие документации.
Убеждается, что ответ содержит ключ homeworks и что его значение является списком.

parse_status(homework):
Извлекает статус домашней работы из ответа API.
Формирует строку для отправки в Telegram на основе статуса.
Проверяет наличие всех обязательных ключей в ответе.

send_message(bot, message):
Отправляет сообщение в Telegram-чат.
Логирует успешную отправку или ошибки.

main():
Основная логика работы программы.
Организует цикл опроса API и отправки уведомлений.
Обрабатывает исключения и логирует ошибки.

### СТЕК
Python 3.9+
pyTelegramBotAPI==4.14.1 — для работы с Telegram API.
requests==2.26.0 — для выполнения HTTP-запросов к API.
python-dotenv==0.20.0 — для загрузки переменных окружения из файла .env.
logging — для логирования работы программы.

### КАК ЗАПУСТИТЬ ПРОЕКТ
Клонировать репозиторий:

```bash
git clone https://github.com/ваш_username/homework_bot.git
cd homework_bot
```
Создать и активировать виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # Для Linux/MacOS
venv\Scripts\activate     # Для Windows
```
Установить зависимости:
```bash
pip install -r requirements.txt
```
Настроить переменные окружения:
Создайте файл .env в корне проекта и добавьте в него следующие переменные:

PRACTICUM_TOKEN=ваш_токен_практикума
TELEGRAM_TOKEN=ваш_токен_бота
TELEGRAM_CHAT_ID=ваш_chat_id

Запустить бота:
```bash
python homework_bot.py
```
ПРИМЕР ЗАПРОСА И ОТВЕТА
Запрос:
```bash
GET /api/homework_statuses
Ответ:
```json
Copy
{
  "homeworks": [
    {
      "id": 123,
      "status": "approved",
      "homework_name": "Домашняя работа 1",
      "reviewer_comment": "Отличная работа!",
      "date_updated": "2023-10-09T15:34:45Z"
    }
  ],
  "current_date": 1696865685
}
```
### АВТОР  
Дмитрий Протасевич  
GitHub: https://github.com/DmitryProtasevich  
Telegram: https://t.me/DmitryProtasevich
