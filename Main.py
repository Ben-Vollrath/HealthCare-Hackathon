import requests
from enum import Enum
from datetime import datetime

from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
import calendar

def sendRequest(start_date,end_date):
        if(start_date == None or start_date == '' or end_date == '' or end_date == None):
            r = requests.get("http://localhost:8080/patientArrival") #Get all Data
        else:
            dt_obj = datetime.strptime(start_date, '%d.%m.%Y')#Time in Milis
            mili_start_date = int(dt_obj.timestamp() * 1000)

            dt_obj = datetime.strptime(end_date, '%d.%m.%Y')#Time in Milis
            mili_end_date = int(dt_obj.timestamp() * 1000)

            r = requests.get("http://localhost:8080/patientArrival?from=" + str(mili_start_date) + "&to=" + str(mili_end_date)) #Get Data in TimeFrame

            
        return r.json()# Return all Data as Json

def getDataOfDay(json_data, day, hospitalID):#Gets the Amount of Transports on a given weekday as average ordered by hour of day
    

    #Get the amount of times given week day has occured in time -> used to calculate average value later
    start_date = currentMillisToDateTime(json_data[0]['created'])
    end_date = currentMillisToDateTime(json_data[-1]['created'])
    countOfDays = [0] * 7
    for weekday in range(0,7):
        countOfDays[weekday] = count_weekdays(start_date,end_date,weekday)
    countOfDay = countOfDays[day]
    
    hours_data_list = [0] * 24 #used to store amount of drives in given hour frame
    for item in json_data:
        milliTime = item['created']
        dateTime = currentMillisToDateTime(milliTime)
        weekDay = dateTime.weekday()


        if(weekDay==day and ( hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID) ) ): # We only need Data from the Weekday we are looking at and correct hospitalID
            hour = dateTime.hour
            hours_data_list[hour] += 1
        #Get the average by dividing through amount of days    

    data = {}

    sonstige = [0] * 24

    for hour in range(0,24):
        hours_data_list[hour] = hours_data_list[hour] / countOfDay if countOfDay > 0 else hours_data_list[hour]

        biggestDepartments = hourlyCountDepartments(weekday,hour, countOfDay,json_data,hospitalID)

        departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1] 
        
        sonstige = hours_data_list[hour] - departmentsum

        
        data[hour] = [["Sonstige ", sonstige],
                        ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                          ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                           ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]
    


def hourlyCountDepartments(weekDay,hour,countOfDay,transportData,hospitalID):
    r = requests.get("http://localhost:8080/departmentCategory") #Get all Data
    json = r.json()#return all data as Jason

    usedDepartmenArr = [0] * (len(json)+1)

    
    for item in transportData:

        milliTime = item['created']
        dateTime = currentMillisToDateTime(milliTime)  #get the weekday from item
        weekDayFromItem = dateTime.weekday()
        hourFromItem = dateTime.hour
        
        departmentCata = item['departmentCategory']
        if departmentCata != None and weekDayFromItem == weekDay and hourFromItem == hour:
            if(hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID)):
                    
                id_value = departmentCata['id']
                usedDepartmenArr[id_value]+=1
    listClone= usedDepartmenArr.copy()
        
    usedDepartmenArr.sort(reverse=True)
    listClone.index(usedDepartmenArr[0])

    dp0, dp1, dp2 = None, None, None

    for item in transportData:
        department = item['departmentCategory']
        if(department == None):
            continue

        if(listClone.index(usedDepartmenArr[0]) == department['id']):
            dp0 = department['name']
        if(listClone.index(usedDepartmenArr[1]) == department['id']):
            dp1 = department['name']
        if(listClone.index(usedDepartmenArr[2]) == department['id']):
            dp2 = department['name']

    out0 = (dp0, usedDepartmenArr[0] / countOfDay) if dp0 is not None else ("No department", 0)
    out1 = (dp1, usedDepartmenArr[1] / countOfDay) if dp1 is not None else ("No department", 0)
    out2 = (dp2, usedDepartmenArr[2] / countOfDay) if dp2 is not None else ("No department", 0)


    return [out0, out1, out2]




def currentMillisToDateTime(currentMillis): #Converts currentMilis Time to Date time
    unix = int(currentMillis) // 1000 # Convert to unix
    dateTime = datetime.fromtimestamp(unix) # Convert to datetime,
    return dateTime

    
def createSum(json_data,average_list,hospitalID):#Creates the average of the sum of trips per day sorted to weekdays

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
    
        if(hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID) ): # If we are filtering for HospitalID, only count up if HospitalID is matching
            average_list[weekDay] = average_list[weekDay] + 1 #Increase count of trips for given day per one
    

    data = {}

    sonstige = [0] * 7  

    #Calculate the average of trips ordered by day, save the averages in data dictionary
    for weekday in range(0,7):
        biggestDepartments = count_departments(weekday,countOfDays[weekday],json_data,hospitalID)

        average_list[weekday] = average_list[weekday] / countOfDays[weekday] if countOfDays[weekday] > 0 else average_list[weekDay]
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

def count_departments(weekDay,countOfDay,transportData,hospitalID):
        countOfDay = 1 if countOfDay <= 0 else countOfDay
        r = requests.get("http://localhost:8080/departmentCategory") #Get all Data
        json = r.json()#return all data as Jason

        usedDepartmenArr = [0] * (len(json)+1)

        

        for item in transportData:

            milliTime = item['created']
            dateTime = currentMillisToDateTime(milliTime)  #get the weekday from item
            weekDayFromItem = dateTime.weekday()
        
            departmentCata = item['departmentCategory']
            if departmentCata != None and weekDayFromItem == weekDay:
                if(hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID)):
                    
                    id_value = departmentCata['id']
                    usedDepartmenArr[id_value]+=1
        listClone= usedDepartmenArr.copy()
        
        usedDepartmenArr.sort(reverse=True)
        listClone.index(usedDepartmenArr[0])

        dp0, dp1, dp2 = None, None, None

        for item in transportData:
            department = item['departmentCategory']
            if(department == None):
                continue

            if(listClone.index(usedDepartmenArr[0]) == department['id']):
                dp0 = department['name']
            if(listClone.index(usedDepartmenArr[1]) == department['id']):
                dp1 = department['name']
            if(listClone.index(usedDepartmenArr[2]) == department['id']):
                dp2 = department['name']

        out0 = (dp0, usedDepartmenArr[0] / countOfDay) if dp0 is not None else ("No department", 0)
        out1 = (dp1, usedDepartmenArr[1] / countOfDay) if dp1 is not None else ("No department", 0)
        out2 = (dp2, usedDepartmenArr[2] / countOfDay) if dp2 is not None else ("No department", 0)


        return [out0, out1, out2]




import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State

app = dash.Dash(__name__)

def plot(data):
    import plotly.express as px
    fig = go.Figure()

    num_tasks_per_day = len(data[0])
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

    colors = px.colors.qualitative.Pastel2 # use the Plotly color palette

    for i in range(num_tasks_per_day):
        fig.add_trace(go.Bar(
            x=weekdays,
            y=[data[day][i][1] for day in data],
            name=data[0][i][0],
            text=[data[day][i][0] for day in data],
            hoverinfo='text+y',
            marker=dict(color=colors[i % len(colors)]), # set the color of the bar
            textfont=dict(size=16), # set the size of the text inside the bars
        ))

    fig.update_layout(
        barmode='stack',
        title='Graphische Darstellung der Krankenfahrten',
        xaxis={'title': 'Wochen Tag', 'titlefont': {'size': 18}}, # set the size of the x-axis title
        yaxis={'title': 'Anzahl von Fahrten', 'titlefont': {'size': 18}}, # set the size of the y-axis title
        showlegend=False
    )

    return fig


app.layout = html.Div([
    html.H1('Interaktives Datendarstellungsmodel zur Datebankintegrierten Datenauferbeitung'),
    dcc.Graph(id='graph'),
    html.Label('Start Date'),
    dcc.Input(id='start-date', type='text', value=''),
    html.Label('End Date'),
    dcc.Input(id='end-date', type='text', value=''),
    html.Label('Hospital ID'),
    dcc.Input(id='hospital-id', type='text', value=''),
    html.Button('Update Graph', id='update-button', n_clicks=0),
], style={'backgroundColor': '#f0f0f0	', 'padding': '20px'})

@app.callback(
    Output('graph', 'figure'),
    Input('update-button', 'n_clicks'),
    State('start-date', 'value'),
    State('end-date', 'value'),
    State('hospital-id', 'value')
)
def update_graph(n_clicks, start_date, end_date, hospital_id):
    if n_clicks > 0:
        sum_list = [0] * 7
        r = sendRequest(start_date, end_date)
        sum_list = createSum(r, sum_list, hospital_id)
        return plot(sum_list)

    # If the button hasn't been clicked, return an empty figure
    return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)

