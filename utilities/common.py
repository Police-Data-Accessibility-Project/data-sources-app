import datetime

def convert_dates_to_strings(data_dict):
    for key, value in data_dict.items():
        if isinstance(value, datetime.date):
            data_dict[key] = value.strftime('%Y-%m-%d')
    return data_dict