#!/bin/bash

# Build the image if needed
docker build -t vmhub-whatsapp .

# Run the test
docker run -it --rm \
  -v $(pwd)/.env:/app/.env \
  --entrypoint python \
  vmhub-whatsapp \
  -m test.test_message