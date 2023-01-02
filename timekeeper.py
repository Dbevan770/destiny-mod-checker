import datetime

# Used to check if the current time is after daily reset time
# Useful for running the bot on a Friday when Xur is not around
async def isTimeBetween (startTime, endTime, nowTime):
    if startTime < endTime:
	    return nowTime >= startTime and nowTime <= endTime
    else:
	    return nowTime >= startTime or nowTime <= endTime

# Check if it is a weekend so we know to look for info on Xur
async def checkIsWeekend(log):
    # If day is currently between 4 (Friday) and 6 (Sunday)
    # ToDo: Add support for Monday until reset as well
    if datetime.datetime.today().weekday() >= 4 and datetime.datetime.today().weekday() <= 6:
        # Additional check on Fridays, Xur will not be around until the reset
        # We need to check if it is after the reset or not when run on Friday
        if datetime.datetime.today().weekday() == 4:
            if await isTimeBetween(datetime.time(18,00), datetime.time(00,00), datetime.datetime.now().time()):
                log.AddLine("It's the weekend!")
                return True
            else:
                return False
        # Outside of the special conditions if it is between those times than it is the weekend
        else:
            log.AddLine("It's the weekend!")
            return True
    # If it is Monday, but not after the daily reset, Xur is still around
    # therefore it is still the weekend and we need to treat it that way
    elif datetime.datetime.today().weekday() == 0:
        if await isTimeBetween(datetime.time(00,00), datetime.time(18,00), datetime.datetime.now().time()):
            log.AddLine("It's the weekend!")
            return True
        else:
            return False
    # If none of this is true, it is a weekday
    else:
        log.AddLine("Another day in the office...")
        return False

# Function that pauses execution of the main loop until a certain time day
def seconds_until(hours, minutes):
    given_time = datetime.time(hours, minutes)
    now = datetime.datetime.now()
    future_exec = datetime.datetime.combine(now, given_time)
    if (future_exec - now).days < 0:  # If we are past the execution, it will take place tomorrow
        future_exec = datetime.datetime.combine(now + datetime.timedelta(days=1), given_time) # days always >= 0

    return (future_exec - now).total_seconds()