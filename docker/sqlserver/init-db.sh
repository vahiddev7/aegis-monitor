#!/bin/bash
set -Eeuo pipefail

: "${DB_NAME:?DB_NAME must be set in .env}"
: "${DB_PASSWORD:?DB_PASSWORD must be set in .env}"
if [[ ! "${DB_NAME}" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "DB_NAME may contain only letters, numbers, and underscores." >&2
  exit 2
fi

SQLCMD="/opt/mssql-tools18/bin/sqlcmd"
until "$SQLCMD" -S db -U sa -P "$DB_PASSWORD" -C -Q "SELECT 1" >/dev/null 2>&1; do
  echo "Waiting for SQL Server to accept connections..."
  sleep 2
done

# Escape closing brackets before using the configured name as a SQL identifier.
escaped_name="${DB_NAME//]/]]}"
"$SQLCMD" -S db -U sa -P "$DB_PASSWORD" -C \
  -Q "IF DB_ID(N'${DB_NAME}') IS NULL CREATE DATABASE [${escaped_name}]"
echo "Database '${DB_NAME}' is ready."
