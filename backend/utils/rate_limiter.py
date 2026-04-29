import time

class RateLimiter:
    def __init__(self, rate_per_sec):
        self.interval = 1 / rate_per_sec
        self.last_time = 0

    def allow(self):
        now = time.time()
        if now - self.last_time < self.interval:
            return False
        self.last_time = now
        return True

    def wait(self):
        while not self.allow():
            time.sleep(0.05)