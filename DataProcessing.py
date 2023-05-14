import requests
from enum import Enum
from datetime import datetime

from datetime import timedelta, date
#from dateutil.relativedelta import relativedelta
import calendar

import constants as c
from TimeConversions import TimeConversions

class DataProcessing:   

    def __init__(self):
        pass

    def sendRequest(self,start_date,end_date):
            if(start_date == None or start_date == '' or end_date == '' or end_date == None):
                r = requests.get(c.API_ADRESS + "patientArrival") #Get all Data
            else:

                mili_start_date = TimeConversions.convertDateTimeToCurrentMillis(start_date)
                mili_end_date =  TimeConversions.convertDateTimeToCurrentMillis(end_date)

                r = requests.get(c.API_ADRESS + "patientArrival?from=" + str(mili_start_date) + "&to=" + str(mili_end_date)) #Get Data in TimeFrame

                
            return r.json()# Return all Data as Json

    def getDataOfDay(self,json_data, day, hospitalID):#Gets the Amount of Transports on a given weekday as average ordered by hour of day
        

        #Get the amount of times given week day has occured in time -> used to calculate average value later
        start_date = TimeConversions.convertCurrentMillisToDateTime(json_data[0]['created'])
        end_date = TimeConversions.convertCurrentMillisToDateTime(json_data[-1]['created'])
        countOfDays = [0] * 7
        for weekday in range(0,7):
            countOfDays[weekday] = self.count_weekdays(start_date,end_date,weekday)
        countOfDay = countOfDays[day]
        
        hours_data_list = [0] * 24 #used to store amount of drives in given hour frame
        for item in json_data:
            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)
            weekDay = dateTime.weekday()


            if(weekDay==day and ( hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID) ) ): # We only need Data from the Weekday we are looking at and correct hospitalID
                hour = dateTime.hour
                hours_data_list[hour] += 1
            #Get the average by dividing through amount of days    

        data = {}

        sonstige = [0] * 24
        for hour in range(0,24):
            hours_data_list[hour] = hours_data_list[hour] / countOfDay if countOfDay > 0 else hours_data_list[hour]
            biggestDepartments = self.hourlyCountDepartments(day,hour, countOfDay,json_data,hospitalID)

            departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1]
            
            sonstige = hours_data_list[hour] - departmentsum

            
            data[hour] = [["Sonstige ", sonstige],
                            ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                            ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                            ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]
        return data
        


    def hourlyCountDepartments(self,weekDay,hour,countOfDay,transportData,hospitalID):
        r = requests.get(c.API_ADRESS + "departmentCategory") #Get all Data
        json = r.json()#return all data as Jason

        usedDepartmenArr = [0] * (len(json)+1)

        
        for item in transportData:

            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)  #get the weekday from item
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




    
        
    def createSum(self,json_data,average_list,hospitalID):#Creates the average of the sum of trips per day sorted to weekdays

        #Get the count of weekdays occuring in given Time Frame
        start_date = TimeConversions.convertCurrentMillisToDateTime(json_data[0]['created'])
        end_date = TimeConversions.convertCurrentMillisToDateTime(json_data[-1]['created'])
        countOfDays = [0] * 7
        for weekday in range(0,7):
            countOfDays[weekday] = self.count_weekdays(start_date,end_date,weekday)
        
        
        #Count amount of trips ordered by day
        for item in json_data:
            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)
            weekDay = dateTime.weekday()
        
            if(hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID) ): # If we are filtering for HospitalID, only count up if HospitalID is matching
                average_list[weekDay] = average_list[weekDay] + 1 #Increase count of trips for given day per one
        

        data = {}

        sonstige = [0] * 7  

        #Calculate the average of trips ordered by day, save the averages in data dictionary
        for weekday in range(0,7):
            biggestDepartments = self.count_departments(weekday,countOfDays[weekday],json_data,hospitalID)

            average_list[weekday] = average_list[weekday] / countOfDays[weekday] if countOfDays[weekday] > 0 else average_list[weekday]
            departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1] 
            
            sonstige[weekday] = average_list[weekday] - departmentsum
            data[weekday] = [["Sonstige ", sonstige[weekday]],
                            ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                            ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                            ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]


        return data


    def count_weekdays(self,start_date, end_date, weekday):
        total = 0
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() == weekday:
                total += 1
            current_date += timedelta(days=1)

        return total

    def count_departments(self,weekDay,countOfDay,transportData,hospitalID):
        countOfDay = 1 if countOfDay <= 0 else countOfDay
        r = requests.get(c.API_ADRESS +  "departmentCategory") #Get all Data
        json = r.json()#return all data as Jason

        usedDepartmenArr = [0] * (len(json)+1)

        for item in transportData:

            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)  #get the weekday from item
            weekDayFromItem = dateTime.weekday()
        
            departmentCata = item['departmentCategory']
            if departmentCata != None and weekDayFromItem == weekDay:
                if(hospitalID == None or hospitalID == '' or item['hospitalId'] == int(hospitalID)):
                    
                    id_value = departmentCata['id']
                    usedDepartmenArr[id_value]+=1

        sortedIndex = self.find_top_three(usedDepartmenArr) #get Index from the 3 Biggest
        usedDepartmenArr.sort(reverse=True)

        dp0, dp1, dp2 = None, None, None
        for item in transportData:
            department = item['departmentCategory']
            if(department == None):
                continue

            elif(sortedIndex[0] == department['id'] and dp0 is None):
                dp0 = department['name']
            elif(sortedIndex[1] == department['id'] and dp1 is None):
                dp1 = department['name']
            elif(sortedIndex[2] == department['id'] and dp2 is None):
                dp2 = department['name']

        out0 = (dp0, usedDepartmenArr[0] / countOfDay) if dp0 is not None else ("No department", 0)
        out1 = (dp1, usedDepartmenArr[1] / countOfDay) if dp1 is not None else ("No department", 0)
        out2 = (dp2, usedDepartmenArr[2] / countOfDay) if dp2 is not None else ("No department", 0)

        return [out0, out1, out2]

    def find_top_three(self,lst):
        # Erstellt eine Liste von Tupeln, die den Index und den Wert aus der ursprünglichen Liste enthalten
        indexed_lst = list(enumerate(lst))

        # Sortiert die Liste in absteigender Reihenfolge nach dem Wert
        sorted_lst = sorted(indexed_lst, key=lambda x: x[1], reverse=True)

        # Gibt die Indizes der ersten drei Elemente der sortierten Liste zurück
        return [i for i, v in sorted_lst[:3]]
