#!/bin/bash

# Generating .dockerignore from .gitignore files:
awk '!/(^\s*#|^\s*$)/ { printf("%s\n", $0) }' .gitignore > .dockerignore
echo '.git' >> .dockerignore
