#!/bin/bash

# Create the .docker.xauth file if it doesn't exist
touch /tmp/.docker.xauth
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -

echo "X11 authentication set up!"
echo "Starting docker-compose now..."

# Run docker-compose in the foreground to allow interaction
docker compose up -d

