start cmd.exe @cmd /c "python server/server_runner.py --verbose 8888 & PAUSE"
start cmd.exe @cmd /c "python client/client_runner.py localhost 8888 & PAUSE"
start cmd.exe @cmd /c "python client/client_runner.py localhost 8888 & PAUSE"
