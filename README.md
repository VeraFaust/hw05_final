# Социальная сеть «Yatube»

## Описание:
Yatube - это социальная сеть.  
В этом проекте было сделано следующее:
- Созданы кастомные страницицы ошибок;
- Возможность добавлять картинки;
- Проверка namespace:name и шаблонов: «Unittest в Django: тестирование Views»
- Тестирование контекста: «Unittest в Django: тестирование views»;
- Дополнительная проверка при создании поста: «Unittest в Django: тестирование Views»;
- Тестирование Forms: «Unittest в Django: тестирование Forms».

## Технологии:
- Python;
- Django;
- Git;
- HTML;
- CSS;
- Bootstrap;
- Django ORM;
- SQL;
- Unittest;
- Pytest.

## Запуск проекта:
- Клонируйте репозиторий:
```
git clone https://github.com/VeraFaust/hw04_tests.git
```

- Установите и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```

- Установите зависимости из файла requirements.txt
```
py -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

- В папке с файлом manage.py запустите миграции:
```
py manage.py makemigrations
```
```
py manage.py migrate
```

- В папке с файлом manage.py создайте админа и запустите проект:
```
py manage.py createsuperuser
```
```
python manage.py runserver
```
Перейти по ссылке:
На сайт http://127.0.0.1:8000/  
В админ-зону http://127.0.0.1:8000/admin

Остановить работу:
```
Ctrl+C
```

## Автор
Вера Фауст
