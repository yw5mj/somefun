#! /bin/bash
#
# Usage:
#   run.sh [ALL_PRICE] [ALL_CATEGORY] [SHEET_NAME=SHEET_NAME]

source $VENV/gcp/bin/activate
python deals.py $@