import math, sys
from datetime import datetime

#   Various date functionalities, regarding julian days
#   From https://gist.github.com/jiffyclub/1294443
#   Slightly modified

def mjd_to_date(mjd):
    """
    mjd_to_date :
        Converts a Modified Julian Date value into a simple calendar date.

    Parameters
    ----------
    mjd : float
        Modified Julian Day value

    Returns
    -------
    year : int
        Year corresponding to parameter MJD
    month : int
        Month corresponding to parameter MJD
    day : float
        Day corresponding to parameter MJD
    """

    jd = mjd + 2400000.5 + 0.5

    F, I = math.modf(jd)
    I = int(I)
    A = math.trunc((I - 1867216.25)/36524.25)

    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I

    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    day = C - E + F - math.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    return year, month, day


def days_to_hmsm(days):
    """
    days_to_hmsm :
        Convert fractional days to hours, minutes, seconds, and microseconds.\n
        Precision beyond microseconds is rounded to the nearest microsecond.

    Parameters
    ----------
    days : float
        A fractional number of days. Must be less than 1.
        
    Returns
    -------
    hour : int
        Hour number.
    min : int
        Minute number.
    sec : int
        Second number.
    micro : int
        Microsecond number.
    """

    hours = days * 24.
    hours, hour = math.modf(hours)
    
    mins = hours * 60.
    mins, min = math.modf(mins)
    
    secs = mins * 60.
    secs, sec = math.modf(secs)
    micro = round(secs * 1.e6)

    return int(hour), int(min), int(sec), int(micro)


def mjd_to_datetime(mjd, isoformat):
    """
    mjd_ISOdatetime :
        From an mjd value, converts its mjd value to its respective date format.

    Parameters
    ----------
    mjd : float
        Modified Julian Day value.
    isoformat : bool
        Flag as to wether result date should be in ISO8601 format or not.

    Returns
    -------
    date : String
        Corresponding date for its 'mjd' as a formatted string parameter.
    """


    year, month, day = mjd_to_date(mjd)
    
    frac_days,day = math.modf(day)
    day = int(day)

    hour,minu,sec,micro = days_to_hmsm(frac_days)

    date = datetime(year, month, day, hour, minu, sec, micro)

    if isoformat:
        return date.isoformat()
        
    return date.strftime('%d/%m/%Y %H:%M:%S:%f')[:-3]
