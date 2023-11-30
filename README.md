# Социальная сеть «Yatube»

## Описание:
Yatube - это социальная сеть.  
В этом проекте было сделано следующее:
- Созданы кастомные страницицы ошибок;
- Возможность добавлять картинки;
- Добавлены тесты;
- Создана система комментариев;
- Добавлена возможность подписки на авторов;
- Добавлено кеширование главной страницы.

## Итог работы над проектом «Yatube»:
Была разработана социальная сеть «Блогикум».
Чтобы написать этот проект, мне нужно было:
- Разобраться в основах HTML и вёрстки для бэкенд-разработчика;
- Создать основу для Django-проекта и добавить в него новые приложения;
- Применить MVC на практике;
- Использовать шаблонизатор Django;
- Освоить Django ORM;
- Написать тесты;
- Задеплоить проект в облако.

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
- Pythonanywhere.

## Запуск проекта:
- Клонируйте репозиторий:
```
git clone https://github.com/VeraFaust/hw05_final.git
```

- Установите и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```

- Установите зависимости из файла requirements.txt:
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

## Ссылки:
- Сайт: http://veronikaf.pythonanywhere.com/
- -Админ-зона: http://veronikaf.pythonanywhere.com/admin

## Автор
Вера Фауст
