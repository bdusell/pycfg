'''A module with some subprocess utilities.'''

import subprocess, os

def eval_command(args, **kwargs):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, **kwargs)
    rc = p.wait()
    if rc != 0: raise EnvironmentError('command failed with exit status %d' % rc)
    return p.stdout.read()

def temp_file(suffix=None):
    return eval_command(['tempfile'] + (['-s', '.' + suffix] if suffix is not None else [])).rstrip()

class TempFile(object):

    def __init__(self, suffix=None):
        self.name = temp_file(suffix)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        os.remove(self.name)

def show_dot(s):
    with TempFile('png') as temp:
        p = subprocess.Popen(['dot', '-Tpng', '-o', temp.name], stdin=subprocess.PIPE)
        p.stdin.write(s)
        p.stdin.close()
        p.wait()
        subprocess.call(['xdg-open', temp.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

