try:
    from .custom_char import Char
except:
    print("Note: custom_char.py does not exist. Using default_char.py")
    from .default_char import Char
