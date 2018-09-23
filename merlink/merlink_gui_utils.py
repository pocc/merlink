# -*- coding: utf-8 -*-
"""GUI utilities not tied to the main application object."""
from PyQt5 import QtCore


class SingleApplication:
    """Determine whether this is a duplicate application.

    Does this by checking a shared memory key.
    Adopted from https://stackoverflow.com/questions/16311396/
    For Anki's method for resolving this, check out
    https://github.com/dae/anki/blob/master/aqt/__init__.py
    """
    def __init__(self, key='memory_condition_key'):
        self._shm = QtCore.QSharedMemory(key)
        if not self._shm.attach():
            if not self._shm.create(1):
                raise RuntimeError('error creating shared memory: %s' %
                                   self._shm.errorString())
        self.condition = False

    def __enter__(self):
        self._shm.lock()
        if self._shm.data()[0] == b'\x00':
            self.condition = True
            self._shm.data()[0] = b'\x01'
        self._shm.unlock()
        return self.condition

    def __exit__(self, exc_type, exc_value, traceback):
        if self.condition:
            self._shm.lock()
            self._shm.data()[0] = b'\x00'
            self._shm.unlock()
