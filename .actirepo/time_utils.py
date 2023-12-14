import os

# check if file1 is newer than file2
def is_newer_than(file1, file2):
    return os.path.isfile(file1) and os.path.getmtime(file2) < os.path.getmtime(file1)
