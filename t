#!/bin/bash
docker compose exec app python ./src/cli.py "$@"