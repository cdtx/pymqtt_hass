#!/usr/bin/env python3
import argparse


def call_config(**kwargs):
    pass

def call_run(**kwargs):
    pass


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser()

    subparsers = main_parser.add_subparsers()

    parser_config = subparsers.add_parser('config')
    parser_config.add_argument('--template', required=True)
    parser_config.add_argument('--print', action='store_true')
    parser_config.set_defaults(func=call_config)

    parser_run = subparsers.add_parser('run')
    #parser_run.add_argument()
    parser_run.set_defaults(func=call_run)

    args = main_parser.parse_args()
    args.func(**vars(args))
