# prediction.py

class PredictionManager:
    def __init__(self):
        self.active = False
        self.current_period = None
        self.direction = None

    def start(self, period, direction):
        self.active = True
        self.current_period = period
        self.direction = direction

    def next(self):
        if self.current_period:
            self.current_period = str(int(self.current_period) + 1)

    def stop(self):
        self.active = False
