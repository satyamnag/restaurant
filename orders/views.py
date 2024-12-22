from django.shortcuts import render, redirect
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from menu.models import FoodItem
from .forms import OrderForm, Order
import simplejson as json
from .utils import generate_order_number
from django.http import HttpResponse, JsonResponse
from .models import Payment, OrderedFood
from app_accounts.utils import send_notification_email
from django.contrib.auth.decorators import user_passes_test
from app_accounts.views import check_role_customer
import razorpay
from project_restaurant.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET


client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# Create your views here.
@user_passes_test(check_role_customer)
def place_order(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('marketplace')
    
    # {'vendor_id':{'subtotal':{'tax_type':{'tax_percentage':'tax_amount'}}}}
    get_tax=Tax.objects.filter(is_active=True)
    vendors_ids=[]
    subtotal=0
    ids={}
    total_data={}
    for item in cart_items:
        if item.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(item.fooditem.vendor.id)
        fooditem=FoodItem.objects.get(pk=item.fooditem.id, vendor_id__in=vendors_ids)
        vendor_id=fooditem.vendor.id
        if vendor_id in ids:
            subtotal=ids[vendor_id]
            subtotal+=(fooditem.price*item.quantity)
            ids[vendor_id]=subtotal
        else:
            subtotal=(fooditem.price*item.quantity)
            ids[vendor_id]=subtotal

        # Calculate the tax_data
        tax_dict={}
        for tax_obj in get_tax:
            tax_type=tax_obj.tax_type
            tax_percentage=tax_obj.tax_percentage
            tax_amount=round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : tax_amount}})

        # Construct total data
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})
    
    subtotal=get_cart_amounts(request)['subtotal']
    total_tax=get_cart_amounts(request)['tax']
    grand_total=get_cart_amounts(request)['grand_total']
    tax_data=get_cart_amounts(request)['tax_dict']
    print(subtotal, total_tax, grand_total, tax_data)
    if request.method=='POST':
        form=OrderForm(request.POST)
        if form.is_valid():
            order=Order()
            order.first_name=form.cleaned_data['first_name']
            order.last_name=form.cleaned_data['last_name']
            order.phone=form.cleaned_data['phone']
            order.email=form.cleaned_data['email']
            order.address=form.cleaned_data['address']
            order.country=form.cleaned_data['country']
            order.state=form.cleaned_data['state']
            order.city=form.cleaned_data['city']
            order.pin_code=form.cleaned_data['pin_code']
            order.user=request.user
            order.total=grand_total
            order.tax_data=json.dumps(tax_data)
            order.total_data=json.dumps(total_data)
            order.total_tax=total_tax
            order.payment_method=request.POST['payment_method']
            order.save()
            order.order_number=generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()

            # RayzorPay Payment
            DATA = {
                "amount": float(order.total) * 100,
                "currency": "INR",
                "receipt": "receipt#"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            razorpay_order=client.order.create(data=DATA)
            razorpay_order_id=razorpay_order['id']
            context={
                'order':order,
                'cart_items':cart_items,
                'razorpay_order_id':razorpay_order_id,
                'RAZORPAY_KEY_ID':RAZORPAY_KEY_ID,
                'rzp_amount':float(order.total) * 100,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

@user_passes_test(check_role_customer)
def payments(request):
    # Check if the request is ajax or not
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method=='POST':

        # Store the payment details in the payment model
        order_number=request.POST.get('order_number')
        transaction_id=request.POST.get('transaction_id')
        payment_method=request.POST.get('payment_method')
        status=request.POST.get('status')

        order=Order.objects.get(user=request.user, order_number=order_number)
        payment=Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=status,
        )
        payment.save()
        # Update the order model
        order.payment=payment
        order.is_ordered=True
        order.save()

        # Move the cart items to the ordered food model
        cart_items=Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food=OrderedFood()
            ordered_food.order=order
            ordered_food.payment=payment
            ordered_food.user=request.user
            ordered_food.fooditem=item.fooditem
            ordered_food.quantity=item.quantity
            ordered_food.price=item.fooditem.price
            ordered_food.amount=item.fooditem.price * item.quantity # total item
            ordered_food.save()

        # Send order confirmation email to the customer
        mail_subject='Thank you for ordering with us.'
        mail_template='orders/order_confirmation_email.html'
        context={
            'user':request.user,
            'order':order,
            'to_email':order.email,
        }
        send_notification_email(mail_subject, mail_template, context)


        # Send order received email to the vendor
        mail_subject='You have received a new order.'
        mail_template='orders/new_order_received.html'
        to_emails=[]
        for item in cart_items:
            if item.fooditem.vendor.user.email not in to_emails:
                to_emails.append(item.fooditem.vendor.user.email)
        print('emails=>', to_emails)
        context={
            'order':order,
            'to_email':to_emails,
        }
        send_notification_email(mail_subject, mail_template, context)
        

        # Clear the cart if the payment is success
        cart_items.delete()

        # Return back to ajax with the status success or failure
        response={
            'order_number':order_number,
            'transaction_id':transaction_id,
        }
        return JsonResponse(response)

    return HttpResponse('Payments view')


def order_complete(request):
    order_number=request.GET.get('order_no')
    transaction_id=request.GET.get('transaction_id')
    try:
        order=Order.objects.get(
            order_number=order_number,
            payment__transaction_id=transaction_id,
            is_ordered=True,
            )
        ordered_food=OrderedFood.objects.filter(order=order)
        subtotal=0
        for item in ordered_food:
            subtotal+=(item.price*item.quantity)

        tax_data=json.loads(order.tax_data)
        print(tax_data)
        context={
            'order':order,
            'ordered_food':ordered_food,
            'subtotal':subtotal,
            'tax_data':tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
    


