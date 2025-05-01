FROM python:3.10-slim-bookworm

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    libdbus-1-3 \
    libgtk-3-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем geckodriver
RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz \
    && tar -xzf geckodriver-v0.34.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm geckodriver-v0.34.0-linux64.tar.gz \
    && geckodriver --version \
    && firefox --version

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt отдельно для кэширования
COPY requirements.txt .

# Устанавливаем Python-зависимости и проверяем установку
RUN pip install --no-cache-dir -r requirements.txt \
    && pip show pyTelegramBotAPI \
    && pip list

# Копируем остальные файлы проекта
COPY . .

# Запускаем скрипт
CMD ["python3", "eq2.py"]