FROM python:3.10

WORKDIR /web

ADD . /web

RUN pip install -r requirements.txt

ENV FLASK_ENV=development

CMD [ "python", "app.py" ]