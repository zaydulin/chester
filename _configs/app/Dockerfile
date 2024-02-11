FROM        python:3.10-slim

ARG NO_CACHE_ARG

ENV         LANG C.UTF-8
ENV         PROJECTPATH=/app/chesterbets
ENV         USER app

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

# Установка разрешений на smtp.py
# Установка разрешений на smtp.py
# Создаем подкаталог перед копированием
RUN mkdir -p ${PROJECTPATH}/_project/settings/
COPY ./_project/settings/smtp.py ${PROJECTPATH}/_project/settings/
RUN chown ${USER} ${PROJECTPATH}/_project/settings/smtp.py \
    && chmod 600 ${PROJECTPATH}/_project/settings/smtp.py

RUN         chown -R ${USER} ${PROJECTPATH}
USER        ${USER}

