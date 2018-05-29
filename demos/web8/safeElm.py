"""
this class exposes only the gtk constants and some of the "safe" classes.
we don't want the server to open pop-ups on the client, so we won't expose
Window() et al.
"""
from efl import elementary as elm

safe_elm_classes = set(("Box","Frame","Entry","Label"))

class SafeElm():
    for _name in dir(elm):
        if _name in safe_elm_classes or _name.isupper():
            exec("exposed_{} = elm.{}".format(_name, _name))
    del _name

SafeElm = SafeElm()

