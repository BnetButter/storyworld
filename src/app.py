# app.py
import sys
import os
import subprocess
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time
import fcntl
import termios
import struct
import os
import pty
import sys
import time
import select

app = Flask(__name__)
socketio = SocketIO(app)
# This must be a global or accessible variable from the socketio event
current_fd = None



@socketio.on('terminal_input')
def handle_terminal_input(data):
    global current_fd
    if current_fd:
        os.write(current_fd, data.encode())

def run_curses_app():
    # Set up the pyte terminal emulator (acting like curses)
    global current_fd
    def set_pty_size(fd, rows, cols):
        size = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

    pid, fd = pty.fork()
    if pid == 0:
        time.sleep(1)
        # In the child process: this sets up the slave side of the pty correctly
        os.execvp("python3", ["python3", "main.py"])
    else:
        set_pty_size(fd, 40, 160)
        try:
            current_fd = fd
            while True:
                r, _, _ = select.select([fd], [], [], 0.1)
                if fd in r:
                    data = os.read(fd, 1024)
                    if not data:
                        continue
                    else:
                        socketio.emit('terminal_output', data)
        except KeyboardInterrupt:
            print("\n[Interrupted]")
        

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    # Start the curses app in a separate thread
    threading.Thread(target=run_curses_app).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
