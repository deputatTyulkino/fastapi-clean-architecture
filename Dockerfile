# syntax=docker/dockerfile:1.7

# ============================================================
# Stage 1: builder — ставим зависимости в изолированный venv.
# Здесь есть компиляторы/dev-заголовки, но они не попадут
# в финальный образ.
# ============================================================
FROM python:3.13-slim-bookworm AS builder

# Не даём pip писать кэш на диск, не генерируем .pyc на этапе установки
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# Системные зависимости, нужные ТОЛЬКО для сборки некоторых пакетов
# (cryptography, bcrypt, argon2-cffi, Pillow — если под вашу платформу/архитектуру
# нет готового manylinux-колеса, pip соберёт из исходников).
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        zlib1g-dev \
        libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Venv собираем отдельно от системного python — так его можно
# целиком скопировать в финальный образ одним слоем
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Сначала только requirements.txt — слой с зависимостями кэшируется
# и не пересобирается при каждом изменении кода приложения
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt


# ============================================================
# Stage 2: runtime — тонкий финальный образ.
# Никаких компиляторов, никаких dev-заголовков, никакого pip-кэша.
# ============================================================
FROM python:3.13-slim-bookworm AS runtime

# Только рантайм-библиотеки, реально нужные установленным пакетам:
#   libjpeg62-turbo, zlib1g — Pillow
#   libffi8                — cffi / argon2-cffi / cryptography
# curl оставлен для healthcheck; можно убрать и делать healthcheck
# средствами самого приложения, если важен каждый мегабайт.
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libffi8 \
        curl \
        tini \
    && rm -rf /var/lib/apt/lists/*

# Непривилегированный пользователь — контейнер никогда не должен
# работать от root в проде
RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Забираем готовый venv из builder-стадии
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    # uvloop подхватится uvicorn'ом автоматически, если он в зависимостях —
    # явно указываем loop, чтобы не гадать в проде
    UVICORN_LOOP=uvloop

WORKDIR /app

# Код копируем отдельным слоем, ПОСЛЕ зависимостей — при изменении
# только исходников пересобирается один этот слой, а не весь venv
COPY --chown=app:app . .

USER app

EXPOSE 8000

# Healthcheck ожидает эндпоинт вида GET /health, отдающий 200.
# Если такого роута ещё нет — обязательно добавь.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# tini как PID 1 — корректно прокидывает сигналы (SIGTERM) в приложение
# и подхватывает зомби-процессы. Критично для graceful shutdown в k8s/compose.
ENTRYPOINT ["tini", "--"]

# Прод-команда: без --reload, без dev-флагов.
# Количество воркеров лучше выносить в переменную окружения (WEB_CONCURRENCY)
# и пробрасывать через compose/k8s, а не хардкодить здесь.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Для Celery worker/beat этот же образ переиспользуется:
# в docker-compose.yml просто переопредели command, например:
#   command: celery -A app.celery_app worker --loglevel=info --concurrency=4
#   command: celery -A app.celery_app beat --loglevel=info
