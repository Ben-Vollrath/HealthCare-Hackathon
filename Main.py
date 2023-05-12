import requests
from enum import Enum
from datetime import datetime

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

def sendRequest(start_date,end_date):
        if(start_date == None or end_date == None):
            r = requests.get("http://localhost:8080/patientArrival") #Get all Data
        else:
            dt_obj = datetime.strptime(start_date, '%d.%m.%Y %H:%M:%S')#Time in Milis
            mili_start_date = int(dt_obj.timestamp() * 1000)

            dt_obj = datetime.strptime(end_date, '%d.%m.%Y %H:%M:%S')#Time in Milis
            mili_end_date = int(dt_obj.timestamp() * 1000)

            r = requests.get("http://localhost:8080/patientArrival?from=" + str(mili_start_date) + "&to=" + str(mili_end_date)) #Get Data in TimeFrame

            
        return r.json()# Return all Data as Json



def currentMillisToDateTime(currentMillis): #Converts currentMilis Time to Date time
    unix = int(currentMillis) // 1000 # Convert to unix
    dateTime = datetime.fromtimestamp(unix) # Convert to datetime,
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

    data = {}

    sonstige = [0] * 7 

    #Calculate the average of trips ordered by day
    for weekday in range(0,7):
        biggestDepartments = count_departments(weekday,countOfDays[weekday],json_data)
        average_list[weekday] = average_list[weekday] / countOfDays[weekday] if countOfDays[weekday] > 0 else 1
        departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1] 
        sonstige[weekday] = average_list[weekday] - departmentsum
        data[weekday] = [["Sonstige ", sonstige[weekday]],
                        ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                          ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                           ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]


    return data


def count_weekdays(start_date, end_date, weekday):
    total = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() == weekday:
            total += 1
        current_date += timedelta(days=1)

    return total

def count_departments(weekDay,countOfDay,transportData):
     r = requests.get("http://localhost:8080/departmentCategory") #Get all Data
     json = r.json()#return all data as Jason

     usedDepartmenArr = [0] * (len(json)+1)

     

     for item in transportData:

        milliTime = item['created']
        dateTime = currentMillisToDateTime(milliTime)  #get the weekday from item
        weekDayFromItem = dateTime.weekday()
       
        departmentCata = item['departmentCategory']

        if departmentCata != None and weekDayFromItem == weekDay:
            id_value = departmentCata['id']
            usedDepartmenArr[id_value]+=1
     listClone= usedDepartmenArr.copy()
    
     usedDepartmenArr.sort(reverse=True)
     listClone.index(usedDepartmenArr[0])



     out1 = (listClone.index(usedDepartmenArr[0]), usedDepartmenArr[0] / countOfDay)
     out2 = (listClone.index(usedDepartmenArr[1]), usedDepartmenArr[1] / countOfDay)
     out3 = (listClone.index(usedDepartmenArr[2]), usedDepartmenArr[2]  / countOfDay)

     return [out1,out2,out3]

def plot(data):
        
    import plotly.graph_objects as go

    fig = go.Figure()

    # Assume that every day has the same number of tasks
    num_tasks_per_day = len(data[0])

    # Create stacked bar for each task
    for i in range(num_tasks_per_day):
        fig.add_trace(go.Bar(
            x=list(data.keys()),
            y=[data[day][i][1] for day in data],
            name=data[0][i][0],
            text=[data[day][i][0] for day in data],
            hoverinfo='text+y',
        ))

    fig.update_layout(
        barmode='stack',
        title='Graphische Darstellung der Krankenfahrten',
        xaxis={'title': 'Wochen Tag'},
        yaxis={'title': 'Anzahl von Fahrten'},
        showlegend=False
    )

    fig.show()



    
def main(start_date,end_date,clinicID):
    sumList = [0] * 7 #Create new List to save sums in hours
    r = sendRequest(start_date,end_date)
    sumList = createSum(r, sumList)
    print(sumList)
    plot(sumList)
    print(sumList)

x = [None] * 10

main(None,None,0)