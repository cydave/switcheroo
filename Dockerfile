FROM python:3.8.3

EXPOSE 10022
WORKDIR /usr/src/app

COPY requirements.txt ./
COPY init.sh ./
RUN pip install --no-cache-dir -r requirements.txt \
        && useradd -r -u 1000 app

COPY . .
RUN chown -R app:app /usr/src/app

USER app
ENTRYPOINT ["./init.sh"]
