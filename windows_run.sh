#!/bin/bash

if [ -z "$1" ]; then
    echo 'You must provide a port'
    exit 1
fi
tmux new -d -s 'deerhunt'
tmux send-keys "server/server_runner.py --verbose $1" C-m
tmux split -v
tmux send-keys "sleep 3 && client/client_runner.py $(hostname) $1" C-m
tmux split -h
tmux send-keys "sleep 1 && test_client/client_runner.py $(hostname) $1" C-m
# tmux next-window

tmux a
