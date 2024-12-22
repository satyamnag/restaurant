from datetime import datetime
import simplejson as json
from django.utils.timezone import now

def generate_order_number(pk):
    current_datetime=now().strftime('%Y%m%d%H%M%S')
    order_number=f'{current_datetime}{pk}'
    return order_number

def order_total_by_vendor(order, vendor_id):
    total_data=json.loads(order.total_data)
    data=total_data.get(str(vendor_id))
    subtotal=0
    tax=0
    tax_dict={}
    for key, value in data.items():
            subtotal+=float(key)
            try:
                value=value.replace("'", '"').strip()
                value = value.replace("Decimal(", "").replace(")", "")
                if value.startswith("{") and value.endswith("}"):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        continue
            except json.JSONDecodeError as e:
                continue
            tax_dict.update(value)

            # Calculate Tax
            for val in value:
                for v in value[val]:
                    tax+=float(value[val][v])
    grand_total=float(subtotal)+float(tax)

    context={
        'subtotal':subtotal,
        'tax_dict':tax_dict,
        'grand_total':grand_total,
    }
    return context