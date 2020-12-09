
class SignalRepeater:
    """
    Repeats full signal end-over-end.
    """
    def __init__(self, li, times):
        self.li = li
        self.times = times
    
    def __len__(self):
        return len(self.li) * self.times
    
    def __getitem__(self, key):
        return self.li[key%len(self.li)]


class SignalDataRepeater:
    """
    Repeats each data point of the signal before moving to next data point.
    """
    def __init__(self, li, times):
        self.li = li
        self.times = times
    
    def __len__(self):
        return len(self.li) * self.times
    
    def __getitem__(self, key):
        return self.li[(key//self.times)%len(self.li)]

