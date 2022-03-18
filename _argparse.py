from argparse import ArgumentParser

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
    return parser


def ArgConflictCheck(args):
    if args.daily:
        if args.service:
            raise ArgumentError("Conflict arguments: --daily, --service")
