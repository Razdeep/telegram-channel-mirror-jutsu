from concurrent.futures import ThreadPoolExecutor
import threading


class SingletonExecutor:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, max_workers=1):
        with cls._lock:
            if cls._instance is None:
                cls._instance = ThreadPoolExecutor(max_workers=max_workers)
        return cls._instance


# # Usage Example
# executor = SingletonExecutor(max_workers=5)
# future = executor.submit(print, "Hello from the singleton class executor!")
