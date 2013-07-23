from lib import events


class _color:
    RESET = '\033[39m\033[0m'
    DEFAULT = '\033[39m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    STRONG = '\033[1m'
    LIGHT = '\033[0m'
    UNDERLINE = '\033[4m'


def info(s):
    # if (not args.quiet):
        events.trigger("console.info", {"message": s})
        print("%s=== %s%s" % (_color.STRONG, s, _color.RESET))


def log_in(s):
    # if (not args.quiet):
        events.trigger("grbl.input", {"message": s})
        print("%s<<< %s%s" % (_color.CYAN, s, _color.RESET))


def log_out(s):
    # if (not args.quiet):
        events.trigger("grbl.output", {"message": s})
        print("%s>>> %s%s" % (_color.GREEN, s, _color.RESET))


def comment(s):
    # if (not args.quiet):
        events.trigger("console.comment", {"message": s})
        print("%s### %s%s" % (_color.STRONG + _color.BLACK, s, _color.RESET))


def debug(s):
    # if(args.verbose and not args.quiet):
        events.trigger("console.debug", {"message": s})
        print("%s!!! %s%s" % (_color.MAGENTA, s, _color.RESET))


def warn(s):
    # if (not args.quiet):
        events.trigger("console.warn", {"message": s})
        print("%s/!\ %s%s" % (_color.YELLOW, s, _color.RESET))
