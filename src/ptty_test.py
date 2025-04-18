import fcntl
import termios
import struct
import os
import pty 
import sys
import time
import select

def set_pty_size(fd, rows, cols):
    size = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

pid, fd = pty.fork()
if pid == 0:
    time.sleep(1)
    # In the child process: this sets up the slave side of the pty correctly
    os.execvp("python3", ["python3", "main.py"])
else:
    set_pty_size(fd, 18, 138)
    try:
        while True:
            r, _, _ = select.select([fd], [], [], 0.1)
            if fd in r:
                data = os.read(fd, 1024)
                if not data:
                    break  # EOF
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
    except KeyboardInterrupt:
        print("\n[Interrupted]")