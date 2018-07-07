FROM python:alpine

ADD requirements.txt /
ADD bot.py /
ADD utils.py /

RUN pip install -r requirements.txt

CMD python bot.py