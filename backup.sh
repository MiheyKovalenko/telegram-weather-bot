#!/bin/bash

# Абсолютный путь до текущей директории
SOURCE_DIR=$(pwd)
BACKUP_DIR="$SOURCE_DIR/last versions/$(date +%Y.%m.%d_%H:%M)"

mkdir -p "$BACKUP_DIR"

# Копирование
cp "$SOURCE_DIR/bot.db" "$BACKUP_DIR/"
cp "$SOURCE_DIR/commands.py" "$BACKUP_DIR/"
cp "$SOURCE_DIR/config.ini" "$BACKUP_DIR/"
cp "$SOURCE_DIR/db.py" "$BACKUP_DIR/"
cp "$SOURCE_DIR/error_log.txt" "$BACKUP_DIR/"
cp "$SOURCE_DIR/functions.py" "$BACKUP_DIR/"
cp "$SOURCE_DIR/log.txt" "$BACKUP_DIR/"
cp "$SOURCE_DIR/main.py" "$BACKUP_DIR/"
cp "$SOURCE_DIR/README.md" "$BACKUP_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$BACKUP_DIR/"
cp -r "$SOURCE_DIR/__pycache__" "$BACKUP_DIR/"
