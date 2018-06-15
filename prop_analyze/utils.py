
def log(msg):
    """
    Log an error message
    :param msg: The message to log
    :return:
    """
    print(msg)


def curr_str_to_float(v: str) -> float:
    """
    Transforms a currency string (like $100.43) into a float
    :param v: The currency string
    :return: the float
    """
    return float(v.strip('$').replace(',', ''))


def float_to_curr(f: float) -> str:
    """
    Transforms a float to a currency string
    :param f: The float
    :return: string
    """
    return '${:,.2f}'.format(f)


def float_to_percent(f: float) -> str:
    """
    Transforms a float to a percent string
    :param f: The float
    :return: string
    """
    return '{:.1%}'.format(f)
