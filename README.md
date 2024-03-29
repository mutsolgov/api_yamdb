# REST API для платформы отзывов

### Описание проекта

REST API - приложение представляет собой социальную платформу, которая собирает отзывы пользователей на произведения.

##### Функциональность

- Аутентификация и авторизация: Пользователи могут регистрироваться, входить в свои аккаунты и получать токены доступа для аутентификации в API.
- Профили пользователей: Пользователи могут создавать свои профили, редактировать информацию о себе.
- Отзывы: Пользователи могут создавать новые отзывы, просматривать отзывы других пользователей, редактировать и удалять свои собственные отзывы.
- Комментарии: Пользователи могут оставлять комментарии к отзывам, отвечать на комментарии и удалять свои собственные комментарии.
- Произведения: Есть список произведений, который может пополнять администраторами или модераторами.
- Категории: Каждое произведение относится к своей категории: фильмы, музыка, кино, сериалы и так далее.
- Жанры: Все произведения в своих категориях разбиты на подгруппы - жанры.

### Технологии

Проект REST API - приложения реализован с использованием следующих технологий и инструментов:

- Django: Популярный фреймворк для разработки веб-приложений на языке Python.
- Django REST Framework: Расширение Django для создания RESTful API.
- База данных: DjangoORM.
- Аутентификация и авторизация: Встроенные механизмы Django для обеспечения безопасности и контроля доступа. Библиотека SimpleJWT.
- Пакеты Python: Дополнительные пакеты Python могут быть использованы для обработки изображений, отправки уведомлений и других функциональных возможностей.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/mutsolgov/api_yamdb.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

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

### Примеры запросов к API

1. Получение списка всех постов:
```
GET /api/v1/titles/{title_id}/reviews/
```
```json
{
	"count": 0,
	"next": "string",
	"previous": "string",
	"results": [
	{
		"id": 0,
		"text": "string",
		"author": "string",
		"score": 1,
		"pub_date": "2019-08-24T14:15:22Z"
	}
]
}
```
2. Добавление новой категории:
```
POST /api/v1/categories/
```
```json
{
	"name": "string",
	"slug": "string"
}
```

3. Получение JWT-токена:
```
POST /api/v1/auth/token/
```
```json
{
	"username": "string",
	"confirmation_code": "string"
}
```
```json
{
	"token": "string"
}
```

### Авторы
- Магомед Муцольгов - [GitHub](https://github.com/mutsolgov)
- Александр Шабалин - [GitHub](https://github.com/WGriimZzW)
- Якимов Роман - [GitHub](https://github.com/Littump)
