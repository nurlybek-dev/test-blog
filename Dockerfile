FROM python:3.9

EXPOSE 8000

WORKDIR /code

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . .

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]
