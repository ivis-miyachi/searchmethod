#!/bin/bash
docker compose exec web python ./src/cli.py "$@"