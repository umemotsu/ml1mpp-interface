import datetime


def parse_optional(string, func):
    if not string:
        return None

    return func(string)


def parse_date(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d").date()
