#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_BASE_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"

# THIS IS NECESSARY TO IMPORT CORRECT SETTINGS
export PLATAFORMA_DJANGO_ENV=production
export DJANGO_SETTINGS_MODULE="Plataforma_de_Vendas.settings"

source ~/miniconda3/etc/profile.d/conda.sh
conda activate conda_env

cd "$PROJECT_BASE_DIR" || {
  echo " Failed to change directory to $PROJECT_BASE_DIR. Aborting."
  exit 1
}

python manage.py cleanup_product_images >> "$PROJECT_BASE_DIR/Products/management/logs/product_image_cleanup.log" 2>&1