#!/bin/bash

docker cp ./backups/backup.sql $(docker compose ps -q db):/backup.sql
docker compose exec db psql -U postgres -d methoddb -f /backup.sql