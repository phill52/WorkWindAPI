from bleach.sanitizer import Cleaner

# Creating a Bleach sanitizer cleaner instance
cleaner = Cleaner()


def sanitizer_string(string):
    string = cleaner.clean(string)
    string = string.strip()
    if string is None or not string:
        raise ValueError("String cannot be None or empty")
    return string
