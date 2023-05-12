import requests
from enum import Enum
from datetime import datetime

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

def sendRequest(start_date,end_date):
        if(start_date or end_date == None):
            r = requests.get("http://localhost:8080/patientArrival") #Get all Data
        else:
            mili_start_date = dt_obj = datetime.strptime(start_date).timestamp() * 1000 #Datetime to militime
            mili_end_date = dt_obj = datetime.strptime(end_date).timestamp() * 1000 #Datetime to militime
            r = requests.get("http://localhost:8080/patientArrivalfrom=" + mili_start_date + "&to" + mili_end_date) #Get Data in TimeFrame
        return r.json()# Return all Data as Json



def currentMillisToDateTime(currentMillis): #Converts currentMilis Time to Date time
    unix = int(currentMillis) // 1000 # Convert to unix
    dateTime = datetime.fromtimestamp(unix) # Convert to datetime
    return dateTime

    
def createSum(json_data,average_list):#Creates the average of the sum of trips per day sorted to weekdays

    #Get the count of weekdays occuring in given Time Frame
    start_date = currentMillisToDateTime(json_data[0]['created'])
    end_date = currentMillisToDateTime(json_data[-1]['created'])
    countOfDays = [0] * 7
    for weekday in range(0,7):
        countOfDays[weekday] = count_weekdays(start_date,end_date,weekday)
    
    
    #Count amount of trips ordered by day
    for item in json_data:
        milliTime = item['created']
        dateTime = currentMillisToDateTime(milliTime)
        weekDay = dateTime.weekday()
        average_list[weekDay] = average_list[weekDay] + 1 #Increase count of trips for given day per one

    #Calculate the average of trips ordered by day
    for weekday in range(0,7):
        average_list[weekday] = average_list[weekday] / countOfDays[weekday]

    return average_list


def count_weekdays(start_date, end_date, weekday):
    total = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == weekday:
            total += 1
        current_date += timedelta(days=1)

    return total
    
def main(start_date,end_date):
    sumList = [0] * 7 #Create new List to save sums in hours
    r = sendRequest(start_date,end_date)
    sumList = createSum(r, sumList)
    print(sumList)


main(None,None)

