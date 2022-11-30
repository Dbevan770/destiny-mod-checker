import os
import datetime

# Defines the way a log file is created
class LogFile:
    data = []
    def __init__(self, _name):
        self.name = _name

    @classmethod
    def AddLine(cls, line):
        print(f'{line}\n')
        LogFile.data.append([datetime.datetime.now(), line])

# Generates the log file at the end of each day
async def generateLogfile(name, data):
    # Stores the filepath to where logs will be kept
    filepath = os.path.join('./logs/', name)

    # Create the new log file and begin writing data to it
    with open(filepath, "w") as f:
        index = 0
        for line in data:
            if index != len(data) - 1:
                f.write(f'[{line[0].strftime("%Y-%m-%d %H:%M:%S")}] {line[1]}')
                f.write("\n")
                index = index + 1
            else:
                f.write(f'[{line[0].strftime("%Y-%m-%d %H:%M:%S")}] {line[1]}')
    
    f.close()