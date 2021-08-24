try:
    from .custom_char import *
except:
    print("Note: custom_char.py does not exist. Using default_char.py")
    from .default_char import *
