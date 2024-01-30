import datetime

long_month = {
    '01' : 'January',
    '02' : 'February',
    '03' : 'March',
    '04' : 'April',
    '05' : 'May',
    '06' : 'June',
    '07' : 'July',
    '08' : 'August',
    '09' : 'September',
    '10' : 'October',
    '11' : 'November',
    '12' : 'December'
}


def get_long_datetime(datetime_in):
    # format will be YYYY-MM-DD HH:MM (ignore after this point)
    datetime_str = str(datetime_in)
    year= datetime_str[0:4]
    month = long_month[datetime_str[5:7]]
    day = datetime_str[8:10]
    time = datetime_str[11:16]
    return f"{day} {month} {year} at {time}"


#dt = datetime.datetime.now()
#print (dt)
#print ('Lets try and format it a little better!')
#long_date = format_datetime(dt)
#print(long_date)




