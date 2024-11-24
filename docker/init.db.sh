#!/bin/sh
# Script para inicializar las bases de datos

# Crear directorios si no existen
mkdir -p /data/chroma
mkdir -p /data/sqlite

# Establecer permisos
chmod -R 777 /data/chroma
chmod -R 777 /data/sqlite

echo "Directorios de bases de datos inicializados"