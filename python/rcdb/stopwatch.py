import timeit


class StopWatchTimer:
    def __init__(self, auto_start=True, func=timeit.default_timer):
        self.elapsed = 0.0
        self._func = func
        self._start = None
        if auto_start:
            self.start()

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None
        return self.elapsed

    def restart(self):
        self.stop()
        result = self.elapsed
        self.reset()
        self.start()

    def reset(self):
        self._start = None
        self.elapsed = 0.0

    @property
    def is_running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
