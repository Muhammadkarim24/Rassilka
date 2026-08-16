# 🤖 Telegram Bot — Рассылки & Подписка на каналы

Telegram-бот на **aiogram 3.x**, который проверяет подписку пользователя на каналы-спонсоры перед доступом к функционалу, а также предоставляет админ-панель со статистикой, списком пользователей и массовой рассылкой.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?style=flat-square&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ✨ Возможности

- 🔐 **Проверка подписки** — доступ к боту открывается только после подписки на все каналы-спонсоры
- 👑 **Админ-панель** — отдельное меню для администратора с инлайн-кнопками
- 📊 **Статистика** — количество пользователей и последний зарегистрированный
- 👥 **Список пользователей** — с прямыми ссылками на профили
- 📢 **Рассылка** — текст, фото, видео, голосовые, документы + опциональная кнопка со ссылкой
- 💾 **Хранение пользователей** — в `CSV`, без базы данных
- 🌐 **Поддержка прокси** — через `aiohttp_socks` (для регионов с ограничениями)

---

## 🗂️ Структура проекта

```
📦 project
├── mainras.py           # точка входа, все хендлеры и логика бота
├── config.py             # список каналов-спонсоров
├── ras_api_token.py       # токен бота и ID администратора (не публикуется!)
├── users.csv              # база пользователей (создаётся автоматически)
└── requirements.txt
```

---

## ⚙️ Установка

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

### 🔑 Настройка

Создайте файл `ras_api_token.py`:

```python
BOT_TOKEN = "ваш_токен_от_BotFather"
ADMIN_ID = 123456789   # ваш Telegram ID (число, без кавычек!)
```

Создайте файл `config.py`:

```python
sponsors = [
    "channel_username_1",
    "channel_username_2",
]
```

*(опционально)* Прокси задаётся переменной окружения:

```bash
set BOT_PROXY=http://user:pass@host:port   # Windows
export BOT_PROXY=http://user:pass@host:port # Linux/macOS
```

---

## ▶️ Запуск

```bash
python mainras.py
```

---

## 🕹️ Команды

| Команда   | Доступ       | Описание                              |
|-----------|--------------|----------------------------------------|
| `/start`  | Все          | Проверка подписки на каналы            |
| `/run`    | Все          | Приветствие (админ видит доп. кнопку) |
| `/admin`  | Только админ | Открыть панель администратора          |

---

## 🛠️ Стек

- [Python 3.11+](https://www.python.org/)
- [aiogram 3](https://docs.aiogram.dev/)
- [APScheduler](https://apscheduler.readthedocs.io/) — для задач по расписанию
- [aiohttp](https://docs.aiohttp.org/) / [aiohttp_socks](https://pypi.org/project/aiohttp-socks/) — поддержка прокси

---

## 📄 Лицензия

Проект распространяется под лицензией MIT — свободно используйте и модифицируйте.
