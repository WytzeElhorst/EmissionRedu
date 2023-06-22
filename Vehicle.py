class Vehicle:
    def __init__(self, size):
        self.size = size

    def capacity(self):
        if self.size == 0:
            return 5
        if self.size == 1:
            return 7
        if self.size == 2:
            return 12


    def emission(self):
        if self.size == 0:
            return 0.06
        if self.size == 1:
            return 0.08
        if self.size == 2:
            return 0.1
