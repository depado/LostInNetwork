# -*- coding: utf-8 -*-


def lock_available(lock):
    free_lock = False
    try:
        free_lock = lock.acquire(blocking=False)
    finally:
        if free_lock:
            lock.release()
            return True
        else:
            return False
