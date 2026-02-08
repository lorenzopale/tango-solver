log = True
debug = True

def timestamp() -> str:
    """
    Returns the current date and time, formatted for an execution log

    Returns (1):
    - Timetag:  string
                Current date and time in the format [YYYY-MM-DD hh:mm:ss]
    """
    from datetime import datetime
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")