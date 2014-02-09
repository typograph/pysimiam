#!/bin/sh
./test_roboloop.py &
sleep 1 && ./test_pcloop.py &
