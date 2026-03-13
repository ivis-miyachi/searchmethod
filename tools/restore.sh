#!/bin/bash

# Usage: ./restore.sh <backup_file.sql.gz>
# 例: ./restore.sh backup_20251111_102019.sql.gz

if [ $# -ne 1 ]; then
	echo "Usage: $0 <backup_file.sql.gz>"
	exit 1
fi

BACKUP_FILE=$1
BASENAME=$(basename "$BACKUP_FILE" .gz)
CONTAINER_DB=$(docker compose ps -q db)

# 1. gzファイルをコンテナにコピー
docker cp "./backups/$BACKUP_FILE" "$CONTAINER_DB":/backups/

# 2. コンテナ内で解凍
docker compose exec db bash -c "gunzip -f /backups/$BASENAME.gz"
docker compose exec db pg_restore --clean -U postgres -d methoddb "/backups/$BASENAME"
# 3. レストア
docker compose exec db pg_restore -U postgres -d methoddb "/backups/$BASENAME"

# 4. コンテナ内のファイル削除
docker compose exec db rm -f "/backups/$BASENAME"