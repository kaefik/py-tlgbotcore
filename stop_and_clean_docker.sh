#!/bin/bash

# Скрипт для удаления контейнера tlgbotcore и образа py-tlgbotcore

# Удаление контейнера tlgbotcore, если он существует
if docker ps -a | grep -q "tlgbotcore"; then
    echo "Остановка и удаление контейнера tlgbotcore..."
    docker stop tlgbotcore >/dev/null 2>&1
    docker rm -f tlgbotcore >/dev/null 2>&1
    echo "Контейнер tlgbotcore удален."
else
    echo "Контейнер tlgbotcore не найден."
fi

# Удаление образа py-tlgbotcore, если он существует
if docker images | grep -q "py-tlgbotcore"; then
    echo "Удаление образа py-tlgbotcore..."
    docker rmi -f py-tlgbotcore >/dev/null 2>&1
    echo "Образ py-tlgbotcore удален."
else
    echo "Образ py-tlgbotcore не найден."
fi

# Дополнительно: очистка неиспользуемых ресурсов (опционально)
# echo "Выполнение очистки неиспользуемых данных Docker..."
# docker system prune -f >/dev/null 2>&1
echo "Очистка завершена."