import argparse
import os


def dir_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise NotADirectoryError(string)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("path_c3d", type=dir_path, help="Input path for c3d file.")
    parser.add_argument("path_usd", type=dir_path, help="Input path for usd file.")
    parser.add_argument("-o", "--output", type=str)
    return parser.parse_args()

if __name__ == "__main__":
    pass