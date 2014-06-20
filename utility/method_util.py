__author__ = 'kevin'


class StepResult(object):
    def __init__(self, succeeded, errorString):
        self.succeeded = succeeded
        self.errorString = errorString

    def __nonzero__(self):
        return self.succeeded