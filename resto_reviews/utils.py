import datetime

def time_now():
    string = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")    
    return '_'.join(string.split(' ')).replace('/', '_')
