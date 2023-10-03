FROM python:3.12-slim

ADD requirements.txt /
ADD bot.py /
ADD utils.py /

RUN pip install -r requirements.txt

CMD python bot.py