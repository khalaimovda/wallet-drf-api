# Wallet DRF API

This is a simple DRF (Django Rest Framework) API for managing wallets and transactions.

According to the original project specifications, we are using Alembic for database migrations.
However, in my personal opinion, the native Django ORM would be more suitable for Django projects.

## Get Started

- Start the application using docker-compose:
```shell
docker-compose up -d 
```

- Access the Swagger documentation for the API at `http://127.0.0.1:8000/swagger`.

- To stop the application, use:
```shell
docker-compose down
```

## Development

- Activate the poetry environment with Python version 3.10:
```shell
PYENV_VERSION=3.10 pyenv exec poetry shell
```

- Install all dependencies:
```shell
poetry install
```

- Start the database:
```shell
docker-compose up db -d
```

- Apply database migrations:
```shell
alembic upgrade head
```

- Run the Django application:
```shell
python wallet/manage.py runserver
```

### Additional commands

- To connect to the local database use:
```shell
mysql -h 127.0.0.1 -P 3306 -u user -p --protocol=TCP
```
(Password: `pass`)


- To run tests, use:
```shell
python wallet/manage.py test wallet
```

- To build a new docker image of the application, use:
```shell
docker build -t image_name -f ./Dockerfile .
```
