def convert_dict_to_fractional_seconds(hours=0, minutes=0, seconds=0, milliseconds=0):
    fractional_seconds = 0.0
    fractional_seconds += milliseconds / 1000.0
    fractional_seconds += seconds
    fractional_seconds += minutes * 60
    fractional_seconds += hours * 60 * 60

    return fractional_seconds

def convert_time_string_to_fractional_seconds(s):
    # Converts eg 0:20:00 to 120.00
    # Format = "hh:mm:ss"

    hours, minutes, seconds = s.split(":")

    return int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
