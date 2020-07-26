FROM python:3.8.3

ENV SW_HOST='0.0.0.0'
ENV SW_PORT='10022'
ENV SW_BANNER='SSH-2.0-OpenSSH_7.4'
ENV SW_DATABASE_URI='/usr/src/app/brain.db'
ENV SW_SERVER_FACTORY='SwitcherooServer'
ENV SW_WORDLIST=/usr/src/app/wordlist.txt

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
