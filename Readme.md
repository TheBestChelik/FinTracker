ps aux | grep script_name
kill PID
nohup python3 script.py > output.log 2>&1 &
