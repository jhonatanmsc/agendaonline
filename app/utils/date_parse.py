from datetime import datetime

import pytz


def datetime_to_str(raw_date):
    timezone = pytz.timezone('America/Sao_paulo')
    dt = datetime.utcfromtimestamp(raw_date / 1000)
    dt = dt.astimezone(timezone)
    return dt.strftime('%d/%m/%Y %H:%M:%S')
