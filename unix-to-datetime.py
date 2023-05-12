from datetime import datetime
unix = int('1680303600000') // 1000
date = datetime.fromtimestamp(unix)
weekday = date.weekday()
print(weekday)