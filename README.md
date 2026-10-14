# Telegram Coupon Bot

Простой бот купонов: менеджер выдаёт, пользователь смотрит баланс и списывает. Управление кнопками (команды тоже работают). Подготовлен под [Bothost](https://bothost.ru/).

## Роли

| Роль | Env | Действия |
|------|-----|----------|
| Менеджер | `MANAGER_ID` | кнопка «Выдать купон» / `/add` |
| Пользователь | `COUPON_USER_ID` | «Баланс», «Списать купон» / `/balance`, `/use` |

Счётчик хранится в `DATA_DIR/coupons.json` (на Bothost по умолчанию `/app/data`).

> Важно: не используйте имя `USER_ID` для получателя — на Bothost эта переменная уже занята платформой.

## Как узнать свой Telegram ID

Напишите [@userinfobot](https://t.me/userinfobot) — он покажет числовой `Id`.

## Локальный запуск (проверка)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# заполните BOT_TOKEN, MANAGER_ID, COUPON_USER_ID
python main.py
```

## Деплой на Bothost

### Вариант A — архив (без Git)

1. Упакуйте файлы (без `.venv`, `.env`, `.git`):

   ```bash
   zip -r coupon-bot.zip main.py requirements.txt README.md
   ```

2. На [bothost.ru](https://bothost.ru/) → создать бота → загрузить архив.
3. Платформа: **Telegram**, библиотека: **aiogram** (или Авто), главный файл: `main.py`.
4. Вставьте токен от BotFather в поле токена (Bothost положит его в `BOT_TOKEN`).
5. В переменных окружения бота добавьте:

   ```text
   MANAGER_ID=111111111
   COUPON_USER_ID=222222222
   ```

6. Задеплойте и откройте логи. Оба человека должны нажать **Start** у бота в Telegram.

### Вариант B — GitHub / GitLab

1. Запушьте этот репозиторий (без `.env`).
2. При создании бота укажите Git URL и ветку `main`.
3. Токен — в форме Bothost; `MANAGER_ID` и `COUPON_USER_ID` — в env панели.

### Сохранение баланса

Пишите данные в `/app/data` (бот уже использует `DATA_DIR`). На бесплатном тарифе Bothost данные могут сбрасываться при перезапуске — для постоянного хранения нужен тариф с volume (Basic/Pro).

## Команды

- `/start` — клавиатура по роли
- `/add` — выдать купон (менеджер)
- `/balance` — баланс
- `/use` — списать один купон (пользователь)
