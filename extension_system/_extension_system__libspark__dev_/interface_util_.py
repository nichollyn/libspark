__author__ = 'kevin'

from easy_import_ import BColors


def raiseMethodNotOverwrittenError(owner, super_class_name, method_name):
    method = owner.__getattribute__(method_name)
    err = "Subclass of '{class_name}' must overwrite a method '{method_name}'\n"\
          .format(class_name=super_class_name,
                  method_name=method_name)
    if method.__doc__:
        docstr = "Method description: " + BColors.CYAN + method.__doc__ + BColors.ENDC
        msg = BColors.YELLOW + err + BColors.ENDC + docstr
    else:
        msg = BColors.YELLOW + err + BColors.ENDC
    raise NotImplementedError(msg)

