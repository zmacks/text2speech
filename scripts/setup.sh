#!/usr/bin/env bash
set -euo pipefail


# Check if env file exists
if [ ! -f .env ] ;
then \
  echo "####################################################################"
  echo "Creating .env file."
  echo "Please edit .env file by following the instructions"
  echo "####################################################################"
  cp .env.local .env 
fi 

# Source env file 
source .env
echo "Sourced env file" 

# Check if IDPS Secret is set
if [ -z $LOCAL_OPENAI_SECRET ];
then \
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"; \
echo "Invalid OPENAI SECRET, please follow instructions in .env file" ; \
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"; \
exit 1; fi

