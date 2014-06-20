__author__ = 'kevin'


class Log(object):
    @staticmethod
    def i(tag, content):
        msg = "I/{0}: {1}".format(tag, content)
        print(msg)

    @staticmethod
    def e(tag, content):
        msg = "E/{0}: {1}".format(tag, content)
        print(msg)

