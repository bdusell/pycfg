'''A module with some subprocess utilities.'''

import subprocess, os, tempfile

def show_dot(s):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            pass
        p = subprocess.Popen(['dot', '-Tpng', '-o', tmp.name], stdin=subprocess.PIPE)
        p.stdin.write(s)
        p.stdin.close()
        p.wait()
        subprocess.call(['xdg-open', tmp.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        if tmp is not None:
            os.remove(tmp.name)

