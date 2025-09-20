from datetime import datetime as dt

# Format: "yyyy:mm:dd:hh:MM:ss"

def toStr(date_time: dt) -> str:
    return f"{date_time.year}:{date_time.month}:{date_time.day}:{date_time.hour}:{date_time.minute}:{date_time.second}"

def fromStr(str_date_time) -> dt:
    year, month, day, hour, minute, second = str_date_time.split(":")
    return dt(int(year), int(month), int(day), int(hour), int(minute), int(second))