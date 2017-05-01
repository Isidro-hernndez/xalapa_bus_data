#!/usr/bin/env python3
import os

if __name__ == '__main__':
    all_folders = set(os.listdir('data'))

    regular_folders = set(filter(
        lambda x: len(os.listdir(os.path.join('data', x)))==4,
        all_folders
    ))

    print('Regular')
    print(sorted(regular_folders))
    print('Weird')
    print(sorted(all_folders-regular_folders))
