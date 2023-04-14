### Статус workflow
![example workflow](https://github.com/lilcorgo/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# Доступ для ревьюера
- http://158.160.11.104/
- логин: ya@ya.ru
- пароль: hello,world

Пересобрал проект
# Foodrgam
 «Продуктовый помощник»: сайт, на котором пользователи публиковуют рецепты, 
 могут добавлять чужие рецепты в избранное и подписываться на публикации 
 других авторов. 
 Сервис «Список покупок» позволяет пользователям создавать список продуктов, 
 которые нужно купить для приготовления выбранных блюд. Список можно выгрузить.

## Как запустить проект локально:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:lilcorgo/foodgram-project-react.git
```


Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
. env/bin/activate
```

```
python3 -m pip install --upgrade pip
```
Перейти в папку бэкенда:
```
cd backend/
```
Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

## Как запустить проект на сервере:

Создать в папке ../infra/ файл .env и заполнить:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

Собрать образ бэкенда:

```
cd ../backend/
docker build -t foodgram .
```

И фронтенда:
```
cd ../frontend/
docker build -t frontend .
```

Запустить контейнеры:
```
cd ../infra/
docker-compose up -d
```

Выполнить миграции:
```
docker-compose exec web python manage.py migrate
```

Создать суперюзера (Администратора):
```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```

## Техническая информация
- Python 3.7.16
- Django 3.2.17
- Django REST Framework 3.14.0
- Djoser 2.1.0
- PostgreSQL
- Docker
- nginx
- gunicorn
## Автор

- [Дитковский Евгений](https://github.com/lilcorgo) 
