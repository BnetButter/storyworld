import os
import pty
import select
import threading
import time
import struct
import fcntl
import termios

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# Store PTY sessions: sid -> {'fd': int, 'pid': int}
clients = {}

def set_pty_size(fd, rows, cols):
    size = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

def run_curses_app(sid):
    pid, fd = pty.fork()
    if pid == 0:
        time.sleep(1)
        os.execvp("python3", ["python3", "main.py"])
    else:
        set_pty_size(fd, 40, 160)
        clients[sid] = {'fd': fd, 'pid': pid}
        try:
            while True:
                r, _, _ = select.select([fd], [], [], 0.1)
                if fd in r:
                    data = os.read(fd, 1024)
                    if not data:
                        break
                    socketio.emit('terminal_output', data, to=sid)
        except Exception as e:
            print(f"[{sid}] Error: {e}")
        finally:
            os.close(fd)
            clients.pop(sid, None)
            print(f"[{sid}] Session closed.")

@socketio.on('connect')
def handle_connect():
    sid = request.sid
    print(f"Client connected: {sid}")
    threading.Thread(target=run_curses_app, args=(sid,), daemon=True).start()

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    print(f"Client disconnected: {sid}")
    client = clients.pop(sid, None)
    if client:
        os.close(client['fd'])

@socketio.on('terminal_input')
def handle_terminal_input(data):
    sid = request.sid
    client = clients.get(sid)
    if client:
        os.write(client['fd'], data.encode())

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
