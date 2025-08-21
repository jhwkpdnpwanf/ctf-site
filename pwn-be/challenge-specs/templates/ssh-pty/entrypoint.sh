#!/bin/sh
printf "Welcome to PTY\n"
while true; do
  read -r line || exit 0
  printf "you said: %s\n" "$line"
done