import jdatetime

def get_formatted_persian_time(format_type="full"):
    """
    Get current time in various formats
    
    Args:
        format_type (str): Format type options:
            - "full": Full date and time with Persian text
            - "date_short": Short date format (YYYY/MM/DD)
            - "date_long": Long date format with day name
            - "time_only": Time only (HH:MM)
            - "time_seconds": Time with seconds (HH:MM:SS)
            - "datetime_iso": ISO datetime format
            - "month_year": Month and year only
            - "year": Year only
            - "weekday": Weekday name only
            - "timestamp": Unix timestamp
    
    Returns:
        str or int: Formatted time string or timestamp
    """
    jdatetime.set_locale(jdatetime.FA_LOCALE)
    now = jdatetime.datetime.now()
    
    formats = {
        "full": "%A %d %B %Y ساعت %H:%M",
        "date_short": "%Y/%m/%d",
        "date_long": "%A %d %B %Y",
        "time_only": "%H:%M",
        "time_seconds": "%H:%M:%S",
        "datetime_iso": "%Y-%m-%d %H:%M:%S",
        "month_year": "%B %Y",
        "year": "%Y",
        "weekday": "%A",
    }
    
    if format_type == "timestamp":
        return int(now.timestamp())
    
    return now.strftime(formats.get(format_type, formats["full"]))
