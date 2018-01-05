from PyQt5.QtGui import QPicture

LOCKED = "res/icons/ic_lock_black_24px.svg"
WHITELIST = "res/icons/ic_people_outline_black_24px.svg"
NO_ENTRY = "res/icons/ic_do_not_disturb_on_black_24px.svg"

_icons_loaded = dict()

def get_icon(path: str) -> QPicture:
    if path in _icons_loaded:
        return _icons_loaded[path]
    pic = QPicture()
    pic.load(path)
    _icons_loaded[path] = pic
    return pic