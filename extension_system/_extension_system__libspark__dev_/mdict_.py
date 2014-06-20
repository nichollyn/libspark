__author__ = 'kevin'


class mdict(dict):
    def __setitem__(self, key, value):
        self.setdefault(key, []).append(value)