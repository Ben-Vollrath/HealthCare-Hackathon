import requests
from datetime import datetime

r = requests.get("http://localhost:8080/patientArrival")
response = r.json()
first_event = response[0]
second_event = response[-1]
print(first_event['created'])
print(second_event['created'])

def currentMillisToDateTime(currentMillis): #Converts currentMilis Time to Date time
    unix = int(currentMillis) // 1000 # Convert to unix
    dateTime = datetime.fromtimestamp(unix) # Convert to datetime
    return dateTime

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

def count_weekdays(start_date, end_date, weekday):
    total = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == weekday:
            total += 1
        current_date += timedelta(days=1)

    return total
    
start_date = currentMillisToDateTime(first_event['created'])
end_date = currentMillisToDateTime(second_event['created'])

count = count_weekdays(start_date,end_date, 0)
print(count)