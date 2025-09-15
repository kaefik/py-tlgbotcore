#!/bin/bash

# Скрипт для удаления Docker контейнера и образа с указанием имен через параметры
# Использование: ./script.sh <имя_образа> <имя_контейнера>

# Проверка количества параметров
if [ $# -ne 2 ]; then
    echo "Ошибка: Необходимо указать два параметра"
    echo "Использование: $0 <имя_образа> <имя_контейнера>"
    echo "Пример: $0 py-tlgbotcore tlgbotcore"
    exit 1
fi

IMAGE_NAME=$1
CONTAINER_NAME=$2

echo "Начало очистки Docker ресурсов"
echo "Образ: $IMAGE_NAME"
echo "Контейнер: $CONTAINER_NAME"
echo "----------------------------------------"

# Удаление контейнера, если он существует
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Остановка и удаление контейнера $CONTAINER_NAME..."
    docker stop "$CONTAINER_NAME" >/dev/null 2>&1
    docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1
    echo "✓ Контейнер $CONTAINER_NAME удален"
else
    echo "Контейнер $CONTAINER_NAME не найден"
fi

# Удаление образа, если он существует
if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
    echo "Удаление образа $IMAGE_NAME..."
    docker rmi -f "$IMAGE_NAME" >/dev/null 2>&1
    echo "✓ Образ $IMAGE_NAME удален"
else
    echo "Образ $IMAGE_NAME не найден"
fi

# Дополнительная очистка (опционально)
echo "----------------------------------------"
read -p "Выполнить очистку неиспользуемых данных Docker? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Выполнение очистки неиспользуемых данных..."
    docker system prune -f
    echo "✓ Очистка завершена"
fi

echo "----------------------------------------"
echo "Готово! Все операции завершены."