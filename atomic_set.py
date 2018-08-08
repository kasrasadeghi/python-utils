"""
This define the atomic_set class, which is an atomic set using threading's Lock.
"""

import threading


class atomic_set:
    def __init__(self):
        self.lock = threading.Lock()
        self.set = set()

    def acquire(self, key: str) -> bool:
        with self.lock:
            if key in self.set:
                return False
            self.set.add(key)
            return True

    def release(self, key: str):
        with self.lock:
            assert key in self.set
            self.set.remove(key)
