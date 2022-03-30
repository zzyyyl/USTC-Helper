from argparse import ArgumentParser
from config import config, LoadConfig, DumpConfig
import json, base64
import os

class ArgumentError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return f"ArgumentError: {self.text}"

def ArgParser():
    parser = ArgumentParser()
    parser.add_argument("--daily", help="run your daily schedule", action='store_true')
    parser.add_argument("-s", "--service", help="service to run", metavar="SERVICE", dest="service")
    parser.add_argument("--silence", help="run in silence", action='store_true')
    parser.add_argument("-u", "--username", help="your student ID", metavar="ID", dest="stuid")
    parser.add_argument("--store-password", help="store password in config", action='store_true')
    parser.add_argument("--config", help="config for services", metavar="CONF")
    return parser


def ArgConflictCheck(args):
    if args.daily:
        if args.service:
            raise ArgumentError("Conflict arguments: --daily, --service")

def ArgInit(args):
    if args.config:
        config["in-command"]["state"] = True
        config["in-command"]["config"] = json.loads(base64.b64decode(args.config.encode()).decode('gbk'))
