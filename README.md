
![Workflow](https://github.com/Hrushon/testcases/actions/workflows/testcases_deploy.yml/badge.svg)

![Python](https://img.shields.io/badge/Python-3.10.9-blue?style=flat&logo=python&logoColor=yellow)
![Django](https://img.shields.io/badge/Django-4.0-red?style=flat&logo=django&logoColor=green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0.1-blueviolet?style=flat&logo=bootstrap&logoColor=blue)

# TestCases ™
## Реализация тестового задания по разработке сервиса для прохождения тестирования пользователями.

В проекте реализованы следующие функции:

+ авторизация и аутентификация пользователей
+ возможность авторизованным пользователям проходить тесты и зарабатывать монеты
+ добавление/удаление тестов и вопросов к ним в админ-панели пользователем с правами "администратор"
+ разделение тестов по тематикам
+ общая таблица с результатами прохождения тестов пользователями
+ изменение цвета фона плашки с логином пользователя за монеты (повышение уровня за счет успешного прохождения тестов)
+ подключены пагинация тестов по одному вопросу на страницу, пагинация итоговой таблицы с результатами пользователей, кеширование
+ неавторизованному пользователю доступно только чтение

## Порядок установки проекта:

Клонируем репозиторий и переходим в директорию с приложением:
```
git clone https://github.com/Hrushon/testcases.git
```
```
cd ./testcases/infra/
```

### Создаем env-файл:

#### _Первый способ (если необходимо изменить имя БД или ещё что то)_:
Создаем и открываем для редактирования файл `.env`:
```
sudo nano .env
```
В файл вносим следующие данные:
```
# секретный ключ для Django
SECRET_KEY="django-insecure-k5gov!n^c^s4(k9%t1%!wzo#kt&34#l=n@k$kwj6&mk^cb%yy0"
# указываем, что работаем с postgresql
DB_ENGINE=django.db.backends.postgresql
# указываем имя базы данных
DB_NAME=postgres
# логин для подключения к базе данных
POSTGRES_USER=postgres
# пароль для подключения к БД
POSTGRES_PASSWORD=postgres
# название сервиса (контейнера) для БД
DB_HOST=db
# указываем порт для подключения к БД
DB_PORT=5432
```

#### _Второй способ (если Вас всё устраивает и так)_:
Просто изменяем название файла `envexample`, находящегося в репозитории данного проекта, на `.env`.

### Развертывание с использованием Docker:

Разворачиваем контейнеры в фоновом режиме:
```
sudo docker-compose up -d
```
При первом запуске выполняем следующие команды:
+ применяем миграции:
```
sudo docker-compose exec testcases python manage.py migrate
```
+ собираем статику:
```
sudo docker-compose exec testcases python manage.py collectstatic --no-input
```
+ загружаем тестовые данные в базу:
```
sudo docker-compose exec testcases python manage.py loaddata data.json
```

### Развертывание локально в режиме разработчика:

Клонируем репозиторий и переходим в директорию с приложением:
```
git clone https://github.com/Hrushon/testcases.git
```
```
cd ./testcases
```
Cоздаем и активируем виртуальное окружение:
```
python -m venv venv
```
```
source venv/Scripts/activate
```
Переходим в директорию с файлом `manage.py`:
```
cd ./testcases
```
Устанавливаем зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
При первом запуске выполняем следующие команды:
+ применяем миграции:
```
python manage.py migrate
```
+ загружаем тестовые данные в базу:
```
python manage.py loaddata data.json
```
Запускаем проект:
```
python manage.py runserver
```

#### Логин и пароль от учетной записи тестового пользователя-администратора:
+ _логин_
```
test
```
+ _пароль_
```
case2023
```