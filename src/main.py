#!/usr/bin/env python3

from src.services.configuration import config


def main():
    print('Version: ' + config['version'])


if __name__ == '__main__':
    main()
