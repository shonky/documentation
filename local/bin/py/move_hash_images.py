#!/usr/bin/env python3

import json
import os
import shutil


def main():
    with open('data/manifests/images.json') as json_file:
        data = json.load(json_file)
        for key, value in data.items():
            src = os.path.abspath("./src/images/" + key)
            dst = os.path.abspath("./static/images/" + value)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)


if __name__ == '__main__':
    main()
