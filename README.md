![example event parameter](https://github.com/Filengun/Foodgramm/actions/workflows/main.yml/badge.svg)

# foodgram-project-react
Foodgram
### Дипломный проект Я.Практикума

## Описание
Приложение «FOODGRAM» - это сайт, где пользователи могут делиться своими рецептами, добавлять рецепты других пользователей в избранное и подписываться на обновления других авторов. Функция «Список покупок» позволяет пользователям составлять список продуктов, необходимых для приготовления выбранных блюд. Также перед походом в магазин можно скачать общий список продуктов для приготовления одного или нескольких выбранных блюд.

### Стек технологий
- [Python 3.7+](https://www.python.org/)
- [Django 2.2.16](https://www.djangoproject.com)
- [djangorestframework 3.12.4](https://www.django-rest-framework.org/)
- [gunicorn 20.0.4](https://docs.gunicorn.org/)
- [NGINX 1.21.3](https://nginx.org/ru/docs/)
- [Docker 4.16.2](https://docs.docker.com/)
- [Docker-compose](https://docs.docker.com/compose/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Yandex.Cloud](https://cloud.yandex.ru/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- [PostgreSQL](https://www.postgresql.org/)
- [Yandex.Cloud](https://cloud.yandex.ru/)

### [Полная документация API (redoc.yaml)](http://51.250.78.250/api/docs/)

### Как заппустить локально
1) Кланируем репозиторий ```git clone git@github.com:Filengun/Foodgramm.git```
2) Создайте файл содержащий переменные виртуального окружения (.env):  ```cd Foodgramm/infra/ touch .env```
3) Собираем образ: 
- ```cd Foodgramm/backend/```
- ```docker build -t <логин на DockerHub>/<название для образа>:<флаг, например версия приложения> ```
4) Собираем контейнеры и выполняем миграции
- ```cd Foodgramm/infra/```
- ```docker-compose up -d или docker-compose up -d --build```
- ```docker-compose exec backend python3 manage.py migrate```
5) Как создать суперюзера
- ```docker-compose exec backend python3 manage.py createsuperuser```
6) Собираем статику 
- ```docker-compose exec backend python3 manage.py collectstatic --no-input```
7) Загружаем информацию в базу данных
- ```docker-compose exec backend python manage.py data_tags```
- ```docker-compose exec backend python manage.py data_ingredients```

### Как заппустить на сервере
1) Поделючаемся к серверу 
- ```ssh <username>@<публичный ip сервера>```
2) Устанавливаем Docker и Docker-Compose- 
- ```apt install docker.io```
- ```apt -y install curl```
- ```curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose```
- ```chmod +x /usr/local/bin/docker-compose```
3) Деплоим проект на сервер
4) Выполняем миграцию 
- ```sudo docker-compose exec backend python3 manage.py migrate```
5) Как создать суперюзера
- ```sudo docker-compose exec backend python3 manage.py createsuperuser```
6) Собираем статику 
- ```sudo docker-compose exec backend python3 manage.py collectstatic --no-input```
7) Загружаем информацию в базу данных
- ```sudo docker-compose exec backend python manage.py data_tags```
- ```sudo docker-compose exec backend python manage.py data_ingredients```

### Про .env
Необходимо обязательно создать папку .env в папке infra и прописать такие параметры
- ```Ваша БД: DB_ENGINE=django.db.backends.postgresql```
- ```Имя БД: DB_NAME=```
- ```Логин для БД: POSTGRES_USER=```
- ```Пароль для этого логина: POSTGRES_PASSWORD=```
- ```Название сервиса (контейнера): DB_HOST=```
- ```Порт для подключения к БД: DB_PORT=```

### Какие API запросы есть в проекте

GET
- ```/api/users/me/```
- ```/api/users/{id}/```
- ```/api/users/```
- ```/api/users/subscriptions/```
- ```/api/tags/```
- ```/api/tags/{id}/```
- ```/api/ingredients/```
- ```/api/ingredients/{id}/```
- ```/api/recipes/```
- ```/api/recipes/?author=1/```
- ```/api/recipes/?tags=breakfast/```
- ```/api/recipes/{id}/```
- ```/api/recipes/download_shopping_cart/```

POST
- ```/api/users/```
- ```/api/users/set_password/```
- ```/api/auth/token/login/```
- ```/api/auth/token/logout/```
- ```/api/users/{id}/subscribe/```
- ```/api/recipes/```
- ```/api/recipes/{id}/favorite/```
- ```/api/recipes/{id}/shopping_cart/```

DELETE
- ```/api/users/{id}/subscribe/```
- ```/api/recipes/{id}/```
- ```/api/recipes/{id}/favorite/```
- ```/api/recipes/{id}/shopping_cart/```

PATCH
- ```/api/recipes/{id}/shopping_cart/```

Пример из запроса
POST api/users/
```
{
  "email": "filengun@mail.ru",
  "first_name": "oleg,
  "last_name": "maslenikov",
  "username": "filengun",
  "password": "12356879"
}
```
POST api/auth/token/login/
```
{
    "email": "filengun@mail.ru",
    "password": "12356879"
}
```
Получаем ответ
```
{
    "auth_token":"846445advae8abg4dzdba6dcda6ca6saeg8avz3a"
}
```

[Олег](https://github.com/Filengun/) - создатель.
