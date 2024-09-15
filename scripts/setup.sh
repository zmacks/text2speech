#!/usr/bin/env bash
set -euo pipefail


# Check if env file exists
if [ ! -f .env ] ;
then \
  echo "Creating .env file..."
  touch .env 
  echo "# Go to https://platform.openai.com/api-keys and 'Create new secret key' to fill this in" >> .env
  echo "OPENAI_API_KEY=" >> .env
  echo "####################################################################"; \
  echo "Invalid OPENAI_API_KEY, please follow instructions in .env file" ; \
  echo "####################################################################"; \
exit 1; fi

# Source env file 
source .env

# Check if secret is set
if [ -z $OPENAI_API_KEY ];
then \
echo "####################################################################"; \
echo "Invalid OPENAI_API_KEY, please follow instructions in .env file" ; \
echo "####################################################################"; \
exit 1; fi

echo "Setup successful!"

