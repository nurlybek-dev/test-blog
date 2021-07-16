```
git clone https://github.com/nurlybek-dev/test-blog.git
```
Перейдя в папку проекта последовательно запустить
```
docker-compose up
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
Сайт будет доступен по локальному адресу на 8000 порту
127.0.0.1:8000
