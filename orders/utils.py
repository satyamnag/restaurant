from datetime import datetime
from django.utils.timezone import now

def generate_order_number(pk):
    current_datetime=now().strftime('%Y%m%d%H%M%S')
    order_number=f'{current_datetime}{pk}'
    return order_number