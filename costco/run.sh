#! /bin/bash
#
# Usage:
#   run.sh [ALL_PRICE] [ALL_CATEGORY] [OUT_FILENAME=FILENAME]

source $VENV/web/bin/activate
python deals.py $@