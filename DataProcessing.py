import requests
from enum import Enum
from datetime import datetime

from datetime import timedelta, date
#from dateutil.relativedelta import relativedelta
import calendar

import constants as c
from TimeConversions import TimeConversions

class DataProcessing:   
    """The class to handle the DataProcessing
    """
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
        
    def countDepartments(self,week_day : int ,transport_data : list ,hour = None ):
        """Gets the count of the three biggest Departments on a given weekday and hour

        Args:
            week_day (int): The weekday to be counted
            transport_data (list): The data to be processed
            hour (_type_, optional): The hour to be counted. Defaults to None.

        Returns:
            _type_: Returns the three biggest departments on a given weekday and hour
        """
        countUsedDepartmentArr = [0] * (len(transport_data)+1) #Array to count the amount of occurences of each department

        for item in transport_data:
            timeData = TimeConversions.convertCurrentMillisToDateTime(item['created'])
            day_of_item = timeData.weekday() #Get the weekday of the item
            hour_of_item = timeData.hour #Get the hour of the item

            department_category = item['departmentCategory']
            if(department_category != None and day_of_item == week_day): #Only count if the item has a department and is on the given weekday
                if(hour == None or (hour != None and hour_of_item == hour) ): #Only count if the item is on the given hour
                    countUsedDepartmentArr[department_category['id']] += 1 #Increasse count of the department by one
        

        sortedIndex = self.find_top_three(countUsedDepartmentArr) #get Index from the 3 Biggest

        countUsedDepartmentArr.sort(reverse=True) #Sort the array to get the 3 biggest departments

        dp0, dp1, dp2 = None, None, None

        for item in transport_data: #Go through all items and get the department name of the 3 biggest departments 
            department = item['departmentCategory']
            if(department == None):
                continue

            if(sortedIndex[0] == department['id']):
                dp0 = department['name']
            if(sortedIndex[1] == department['id']):
                dp1 = department['name']
            if(sortedIndex[2] == department['id']):
                dp2 = department['name']
        
        #Return the 3 biggest departments names and their count
        out0 = [dp0, countUsedDepartmentArr[0]] if dp0 is not None else ("No department", 0)
        out1 = [dp1, countUsedDepartmentArr[1]] if dp1 is not None else ("No department", 0)
        out2 = [dp2, countUsedDepartmentArr[2]] if dp2 is not None else ("No department", 0)

        return [out0, out1, out2]
    
    def getDataOfWeekOrDay(self, transport_data : list, return_list : list, week_day : int):
        """Gets the Data of a Week or Hour

        Args:
            transport_data (list): THe data to be processed
            return_list (list): The list to be filled with the data must be size 24 for hours and 7 for week
            week_day (int): The weekday to be counted (only when return_list is size 24)

        Returns:
            _type_: Returns the data of a week or hour | Data is averaged
        """

        
        countOfDays = self.countOccurencesOfDays(transport_data)
        return_list_len = len(return_list)

        for item in transport_data:
            milliTime = item['created']
            dateTime = TimeConversions.convertCurrentMillisToDateTime(milliTime)
            weekDay = dateTime.weekday()

            #Count amount of trips ordered by day/hour
            if(return_list_len == 24): #If we want the data ordered by hours
                if(weekDay==week_day): # Only get data from given weekday
                    hour = dateTime.hour
                    return_list[hour] += 1

            elif(return_list_len == 7):#If we want the data ordered by weekdays
                return_list[weekDay] += 1
        
        return_dic = {}

        sonstige = [0] * return_list_len
        for x in range(0, return_list_len): #Go through list
            
            #Get the 3 biggest departments
            biggestDepartments = self.countDepartments(week_day if return_list_len == 24 else x , transport_data , x if return_list_len == 24 else None) #Get the 3 biggest departments
            

            #Get the average of the data
            return_list[x] = return_list[x] / (countOfDays[x] if return_list_len == 7 else countOfDays[week_day])

            #Get the average of the departments
            for i in range(0, len(biggestDepartments)):
                biggestDepartments[i][1] = biggestDepartments[i][1] / (countOfDays[x] if return_list_len == 7 else countOfDays[week_day])


            sum_of_departments = biggestDepartments[0][1] + biggestDepartments[1][1] + biggestDepartments[2][1]

            #Get average of sonstige by sum of all trips - sum of the 3 biggest departments
            sonstige = return_list[x] - sum_of_departments

            #Add the data to the return dic
            return_dic[x] = [["Sonstige ", sonstige],
                            ["Abteilung " + str(biggestDepartments[0][0]), biggestDepartments[0][1]],
                            ["Abteilung " + str(biggestDepartments[1][0]), biggestDepartments[1][1]],
                            ["Abteilung " + str(biggestDepartments[2][0]), biggestDepartments[2][1]]]
        
        return return_dic

    def getDataOfDay(self,json_data, week_day):
        """Gets the Data of a Day

        Args:
            json_data (_type_): The data to be processed
            week_day (_type_): The weekday to be counted

        Returns:
            _type_: Returns the data of a day
        """
        return_list = [0] * 24 #24 hours in a day
        return self.getDataOfWeekOrDay(json_data, return_list, week_day)           

    def getDataOfWeek(self,json_data):
        """Gets the Data of a Week

        Args:
            json_data (_type_): The data to be processed

        Returns:
            _type_: Returns the data of a week
        """
        return_list = [0] * 7 #7 days in a week
        return self.getDataOfWeekOrDay(json_data, return_list, None)

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
