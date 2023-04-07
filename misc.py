def try_cast(x, to_type: __build_class__, default=None):
    """
    tries cast value to type
    :param x: value
    :param to_type: cast type
    :param default: default return value
    :return: if success -> converted value, else -> default
    """
    try:
        return to_type(x)
    except (ValueError, TypeError) as e:
        return default


def load_file(path, mode="r+"):
    with open(path, mode) as f:
        content = f.read()
    return content
