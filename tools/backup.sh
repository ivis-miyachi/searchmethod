#!/bin/bash

now=$(date +%Y%m%d_%H%M%S)
docker compose exec db pg_dump -U postgres -F c -b -v -f /backups/backup_$now.dump methoddb
docker cp $(docker compose ps -q db):/backups/backup_$now.dump ./backups/