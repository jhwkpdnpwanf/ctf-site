#!/bin/sh
while true; do
  printf "ready\n" | socat -v -T5 -d -d TCP-LISTEN:31337,reuseaddr,fork -
done