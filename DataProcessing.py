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
        """Sends Request to the API and returns the Data as Json

        Args:
            start_date (_type_): The Start date of the time frame | If None, earlierst date is used
            end_date (_type_): The End Date of the time frame | If None, latest date is used

        Returns:
            _type_: Returns the Data List filled with Dicts
        """
        mili_start_date = TimeConversions.convertDateTimeToCurrentMillis(start_date) if (start_date != None and start_date != '') else ''
        mili_end_date =  TimeConversions.convertDateTimeToCurrentMillis(end_date) if (end_date != None and end_date != '') else ''

        r = requests.get(c.API_ADRESS + "patientArrival?from=" + str(mili_start_date) + "&to=" + str(mili_end_date)) #Get Data in TimeFrame

        return r.json()

    def filterData(self, json_data : list, filter_criteria : str, filter_value):
        """Return all Data from json_data that fits the filter criteria

        Args:
            json_data (_type_): The json data to be filtered
            filter_criteria (_type_): The filter criteria
            filter_value (_type_): The filter value
        Returns:
            _type_: Returns the filtered data list
        """
        filtered_data = [x for x in json_data if x[filter_criteria] == filter_value] #Only adds new Elements to the list if they fit the filter criteria
        return filtered_data
            
    def countOccurencesOfDays(self, json_data : list):
        """Counts the amount of occurences of each weekday in the time frame

        Args:
            json_data (_type_): The json data to be processed

        Returns:
            _type_: Returns a list containing the amount of occurences of each weekday
        """
        start_date = TimeConversions.convertCurrentMillisToDateTime(json_data[0]['created']) #The first in date in Dataset
        end_date = TimeConversions.convertCurrentMillisToDateTime(json_data[-1]['created']) #The last date in Dataset

        countOfDays = [0] * 7
        for weekday in range(0,7):
            countOfDays[weekday] = self.count_weekdays(start_date,end_date,weekday)

        return countOfDays

    def count_weekdays(self,start_date, end_date, weekday):
        """Count the amount of occurences of a given weekday in a given time frame

        Args:
            start_date (_type_): The Start date of the time frame
            end_date (_type_):  The End date of the time frame
            weekday (_type_): The Weekday to be counted

        Returns:
            _type_: Returns the count of weekdays
        """
        total = 0
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() == weekday:
                total += 1
            current_date += timedelta(days=1)

        return total

    def getDataOfDay(self,json_data, week_day):#Gets the Amount of Transports on a given weekday as average ordered by hour of day
        """Gets the Average Amount of Transports per department on a given week_day ordered by hours of day

        Args:
            json_data (_type_): The Json Data to be processed
            week_day (_type_): The WeekDay to be processed

        Returns:
            _type_: Returns a dict containing the average amount of transports per department on a given weekday ordered by hours of day
        """

        #Get the amount of times given week day has occured in time -> used to calculate average value later
        countOfDays = self.countOccurencesOfDays(json_data)
        countOfDay = countOfDays[week_day]
        
        hours_data_list = [0] * 24 #used to store amount of drives in given hour frame


        for item in json_data:
            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)
            weekDay = dateTime.weekday()

            if(weekDay==week_day): # We only need Data from the Weekday we are looking at and correct hospitalID
                hour = dateTime.hour
                hours_data_list[hour] += 1
            #Get the average by dividing through amount of days    

        data = {}

        sonstige = [0] * 24
        for hour in range(0,24):
            hours_data_list[hour] = hours_data_list[hour] / countOfDay if countOfDay > 0 else hours_data_list[hour]
            biggestDepartments = self.hourlyCountDepartments(week_day,hour, countOfDay,json_data)

            departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1]
            
            sonstige = hours_data_list[hour] - departmentsum

            
            data[hour] = [["Sonstige ", sonstige],
                            ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                            ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                            ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]
        return data
        
    def hourlyCountDepartments(self,weekDay,hour,countOfDay,transportData):
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

    def createSum(self,json_data,average_list):#Creates the average of the sum of trips per day sorted to weekdays

        #Get the count of weekdays occuring in given Time Frame
        countOfDays = self.countOccurencesOfDays(json_data)
                
        #Count amount of trips ordered by day
        for item in json_data:
            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)
            weekDay = dateTime.weekday()
            average_list[weekDay] = average_list[weekDay] + 1 #Increase count of trips for given day per one
        

        data = {}

        sonstige = [0] * 7  

        #Calculate the average of trips ordered by day, save the averages in data dictionary
        for weekday in range(0,7):
            biggestDepartments = self.count_departments(weekday,countOfDays[weekday],json_data)

            average_list[weekday] = average_list[weekday] / countOfDays[weekday] if countOfDays[weekday] > 0 else average_list[weekday]
            departmentsum = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1] 
            
            sonstige[weekday] = average_list[weekday] - departmentsum
            data[weekday] = [["Sonstige ", sonstige[weekday]],
                            ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                            ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                            ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]


        return data

    def count_departments(self,weekDay,countOfDay,transportData):
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
        """Gets the 3 biggest elements in a list

        Args:
            lst (_type_): The list to be searched

        Returns:
            _type_: Returns the indices of the 3 biggest elements in the list
        """
        # Erstellt eine Liste von Tupeln, die den Index und den Wert aus der ursprünglichen Liste enthalten
        indexed_lst = list(enumerate(lst))

        # Sortiert die Liste in absteigender Reihenfolge nach dem Wert
        sorted_lst = sorted(indexed_lst, key=lambda x: x[1], reverse=True)

        # Gibt die Indizes der ersten drei Elemente der sortierten Liste zurück
        return [i for i, v in sorted_lst[:3]]
