FROM python:3.8-slim-buster
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 5000
ADD . .
ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
