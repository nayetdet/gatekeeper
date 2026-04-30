#!/usr/bin/env bash
set -euo pipefail

readonly DEFAULT_COMPOSE_FILE="docker-compose.yml"
readonly DEFAULT_COMPOSE_ENV_FILES=".env"

export COMPOSE_FILE="${COMPOSE_FILE:-$DEFAULT_COMPOSE_FILE}"
export COMPOSE_ENV_FILES="${COMPOSE_ENV_FILES:-$DEFAULT_COMPOSE_ENV_FILES}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --docker-compose)
      export COMPOSE_FILE="${2:-}"
      shift 2
      ;;
    --env-file)
      export COMPOSE_ENV_FILES="${2:-}"
      shift 2
      ;;
    *)
      echo "Error: unknown option: $1"
      exit 1
      ;;
  esac
done

if [ ! -f "${COMPOSE_FILE}" ]; then
  echo "Error: docker compose file not found"
  exit 1
fi

if [ ! -f "${COMPOSE_ENV_FILES}" ]; then
  echo "Error: env file not found"
  exit 1
fi

if [ "$(docker info --format '{{.Swarm.LocalNodeState}}')" != "active" ]; then
  docker swarm init
fi

mkdir -p data
docker stack deploy \
  --prune \
  --detach \
  --with-registry-auth \
  --resolve-image always \
  --compose-file <(docker compose config | sed -E '/^name:/d; s/(size|published): "([0-9]+)"/\1: \2/') \
  gatekeeper
