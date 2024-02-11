FROM        python:3.10-slim

ENV         LANG C.UTF-8
ENV         PROJECTPATH=/app/chesterbets
ENV         USER app
# Создаем подкаталог перед копированием
RUN mkdir -p /app/chesterbets/_project/settings/

# Устанавливаем права доступа к директории
RUN chown -R app /app/chesterbets/_project/settings/

RUN         set -x && apt-get -qq update \
            && apt-get install -y --no-install-recommends \
            libpq-dev python3-dev \
            && apt-get purge -y --auto-remove \
            && rm -rf /var/lib/apt/lists/*

WORKDIR     ${PROJECTPATH}

RUN         useradd -m -d /home/${USER} ${USER} \
            && chown -R ${USER} /home/${USER} \
            && chown -R ${USER} /app

ADD         https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait ${PROJECTPATH}/wait
RUN         chmod +x ${PROJECTPATH}/wait

COPY        requirements.txt ${PROJECTPATH}
RUN         pip install --no-cache-dir -r ${PROJECTPATH}/requirements.txt

COPY        ./src/* ${PROJECTPATH}

RUN         chown -R ${USER} ${PROJECTPATH}
USER        ${USER}




