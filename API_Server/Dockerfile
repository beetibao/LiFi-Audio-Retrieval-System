FROM python:3.10

WORKDIR /server

ADD . /server

ENV FLASK_ENV=development

ENV FLASK_APP=run.py 

RUN pip install -r requirements.txt

CMD [ "python", "run.py" ]