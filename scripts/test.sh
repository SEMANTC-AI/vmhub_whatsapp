#!/bin/bash

# Build the image if needed
docker build -t vmhub-whatsapp .

# Run the test with environment variables from .env file
docker run -it --rm \
  --env-file .env \
  vmhub-whatsapp \
  python -m test.test_message