#! /bin/bash
#
# Usage:
#   run.sh [ALL_PRICE] [ALL_CATEGORY]

source $VENV/web/bin/activate
python deals.py $@