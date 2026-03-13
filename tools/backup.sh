#!/bin/bash

now=$(date +%Y%m%d_%H%M%S)
docker compose exec db mkdir -p /backups
docker compose exec db pg_dump -U postgres -F c -b -v -f /backups/backup_$now.sql methoddb
docker cp $(docker compose ps -q db):/backups/backup_$now.sql ./backups/
gzip ./backups/backup_$now.sql