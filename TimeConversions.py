from datetime import datetime

from datetime import timedelta, date
#from dateutil.relativedelta import relativedelta
import calendar

class TimeConversions:

    @staticmethod
    def convertCurrentMillisToDateTime(currentMillis): #Converts currentMilis Time to Date time
        unix = int(currentMillis) // 1000 # Convert to unix
        dateTime = datetime.fromtimestamp(unix) # Convert to datetime,
        return dateTime
    
    def convertDateTimeToCurrentMillis(dateTime):
        dt_obj = datetime.strptime(dateTime, '%d.%m.%Y')
        return int(dt_obj.timestamp() * 1000)
