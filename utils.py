import platform
import time
from datetime import datetime


def get_system_information(only_os: bool = False) -> str:
    if only_os:
        return platform.system()
    return f"{platform.system()} ({platform.platform()}, {platform.machine()}) - Python {platform.python_version()}"


def timestamp_now(compact=False, only_ymd=False) -> str:
    """Returns a string of the current date+time in the form of
        YYYY-MM-DD hh:mm:ss
    If `compact` == True, then returns in the form of
        YYYYMMDD_hhmmss
    If `only_ymd` == True, then only the first "year/month/day" portion is returned:
        YYYY-MM-DD or YYYYMMDD
    """
    timestamp = datetime.now()
    if compact:
        if only_ymd:
            return timestamp.strftime("%Y%m%d")
        return timestamp.strftime("%Y%m%d_%H%M%S")
    if only_ymd:
        return timestamp.strftime("%Y-%m-%d")
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def get_system_timezone(account_for_daylight_savings: bool = True) -> str:
    """Returns the current timezone of the system this script is running on.
    If `account_for_daylight_savings` == True, then a more specific daylight savings timezone is returned instead.
        Example: "Pacific Standard Time" versus "Pacific Daylight Time"
    """
    dst_selector = 0
    if account_for_daylight_savings:
        # https://docs.python.org/3/library/time.html#time.struct_time
        dst_selector = time.localtime().tm_isdst
    # https://docs.python.org/3/library/time.html#time.tzname
    return time.tzname[dst_selector]
