from datetime import datetime

from datetime import timedelta, date
#from dateutil.relativedelta import relativedelta
import calendar

class TimeConversions:

    @staticmethod
    def convertCurrentMillisToDateTime(currentMillis):
        """Converts currentMilis Time to Date time

        Args:
            currentMillis (int): The current time in milliseconds

        Returns:
            datetime: Returns the current time as datetime
        """
        unix = int(currentMillis) // 1000 # Convert to unix
        dateTime = datetime.fromtimestamp(unix) # Convert to datetime,
        return dateTime
    
    def convertDateTimeToCurrentMillis(dateTime):
        """Converts a datetime to currentMillis

        Args:
            dateTime (datetime): The datetime to be converted

        Returns:
            int: Returns the current time in milliseconds
        """
        dt_obj = datetime.strptime(dateTime, '%d.%m.%Y')
        return int(dt_obj.timestamp() * 1000)
