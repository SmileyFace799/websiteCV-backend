from datetime import datetime as dt, timedelta as td
from random import randint
from portalocker import portalocker, LOCK_EX
import json
import dateTmeStr

with open("secretData/key_info.json", "r") as f:
    KEY_INFO = json.load(f)
    
def intify(s: str):
    if s == "":
        return 0
    s = s.strip()
    if not s.isdigit():
        print(f"Error: \"{s}\" is not recognized as a number, defaulting to 0")
    return int(s) if s.isdigit() else 0


months = intify(input("How many months should the generated key be valid (1 month = 30 days)? "))
days = intify(input("How many days should the generated key be valid? "))
hours = intify(input("How many hours should the generated key be valid? "))
minutes = intify(input("How many minutes should the generated key be valid? "))

expiry = dt.now() + td(days=months * 30 + days, hours=hours, minutes=minutes)
key = ''.join(KEY_INFO["chars"][randint(0, len(KEY_INFO["chars"]) - 1)] for _ in range(KEY_INFO["length"]))

with open("secretData/keys.json", "r") as f:
    portalocker.lock(f, LOCK_EX)
    try:
        newJson = json.load(f) + [{"key": key, "expiry": dateTmeStr.toStr(expiry)}]
    finally:
        portalocker.unlock(f)
with open("secretData/keys.json", "w") as f:
    portalocker.lock(f, LOCK_EX)
    try:
        json.dump(newJson, f, indent=4)
    finally:
        portalocker.unlock(f)

print(f"Generated key: {key}\nValid until: {expiry}")
