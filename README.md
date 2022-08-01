## Проект YaTube

YaTube это сайт социальной сети для блогеров с возможностью публикации и редактирования записей. В рамках проекта реализовано кэширование - работает на главной странице и обновляется раз в 20 секунд. Для проекта написаны unit-тесты.

Функционал проекта:
1) Регистрация новых пользователей.
2) Создание и редактирование своих записей с возможностью публикации фотографий.
3) Группировка записей по сообществам.
4) Просматривание страниц других авторов.
5) Комментирование записей других авторов.
6) Подписка на авторов.
7) Администратор сайта имеет ввозможность создания групп, модерации записей и работы с пользователями.

## Стек технологий

Python 3.9
Django 2.2.16
Pillow 8.3.1
SQLite
Bootstrap

## Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/AxelVonReems/hw05_final.git
```

Перейти в папку с проектом

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
WIN: python -m venv venv
MAC: python3 -m venv venv
```

```
WIN: source venv/scripts/activate
MAC: source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
WIN: python -m pip install --upgrade pip
MAC: python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
WIN: python manage.py migrate
MAC: python3 manage.py migrate
```

Запустить проект:

```
WIN: python manage.py runserver
MAC: python3 manage.py runserver
```

Перейти по адресу http://127.0.0.1:8000
