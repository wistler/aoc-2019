import sys, os, time, datetime

class Progress:
    indicator = ['>', 'v', '<', '^', '.', '*']
    def __init__(self, total):
        self.total = total
        self.count = 0
        self.start_time = time.time()
        self.last_update = time.time()
        self.index = 0

    def add(self, steps, forceReport=False):
        self.count += steps
        now = time.time()
        if forceReport or self.get()%1 == 0 or now - self.last_update > 0.2:
            estimated_time_left = (now - self.start_time) * (100 - self.get()) / self.get() 
            eta = 'ETA {}'.format(datetime.timedelta(seconds=int(estimated_time_left)))
            print("\r{} {:6.2f}% {}".format(Progress.indicator[self.index], self.get(), eta),
                  end='')
            self.last_update = now
            self.index = (self.index + 1) % len(Progress.indicator)

    def clear(self):
        print('\r'+(' ' * 75), end='\r')

    def get(self):
        return (self.count*100)/self.total

    def __str__(self):
        return str(self.get()) + '%'
    