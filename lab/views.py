
"""
HiveFusion Lab - Cybersecurity Tools for Everyone
Copyright © 2025 HiveFusion Lab.
All rights reserved.

Website: https://www.hivefusion.in
License: Proprietary — Unauthorized copying, modification, or distribution of this file is strictly prohibited without written consent.
Author: HiveFusion Lab Development Team
"""

import logging
import re
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render
from django.contrib import messages
from .models import ContectForm
from django.http import JsonResponse
from core.language import contectyou, m, NameToBig, EmptyFields, MethodNotAllowed, ServerErorr , SUCCESS_TRUE, ErrorBar , EmailNotValid, PRODUCT_INFO, address_prpu , ToManyattempts , ShippingPrice , MinimamOrderPrice ,  FieldRequired
import json
from .models import EmailAlertForUpcomingProduct
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from accounts.models import CartItem , CustomUser
from django.utils.html import escape
from baniya.models import Order
from django.db import DatabaseError, IntegrityError
from django.core.exceptions import ValidationError


logging.basicConfig(level=logging.INFO, filename="WhySoSerious.log" , filemode='w' , format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d | %(funcName)s() -> %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
import time

logger = logging.getLogger(__name__)

PHONE_RE = re.compile(r'^\+?\d{7,15}$')

default = True 


def homepage(request):
    if request.method == 'POST':
        data = request.POST
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')


        if name is not None and email is not None and message is not None:
            if len(name) < 150:
                ContectForm.objects.create(
                    name=name,
                    email= email,
                    message= message
                )
                return JsonResponse({m : contectyou})
            else:
                return JsonResponse({m: NameToBig})
        else:
            return JsonResponse({m: EmptyFields})
    

    return render(request , 'index.html')

def aboutpage(request):
    return render(request, 'about.html')

def cartpage(request):
    return render(request, 'cart.html')


def pocketMiniPage(request):
    return render(request , 'hivefusion-lab-pocket-mini.html')

def ConsolePage(request):
    return render(request , 'hivefusion-lab-console.html')

def UserEnroll(request):
    """
    Handles user enrollment for email alerts for upcoming products.

    This function processes POST requests to enroll a user's email for alerts.
    It expects a JSON payload in the request body containing the user's email.
    The view performs several validation checks on the provided email address:
    - It ensures the request method is POST.
    - It checks if the 'email' field is present in the JSON data.
    - It validates the email format using Django's built-in `validate_email`.
    If the email is valid and all checks pass, it creates a new
    `EmailAlertForUpcomingProduct` object in the database.

    Args:
        request: The HTTP request object.

    Returns:
        A JsonResponse with the result of the operation.
        - Returns a success JSON response if the email is successfully saved.
        - Returns a JSON response with an error message and a 400-level status code
            for validation failures (e.g., empty or invalid email).
        - Returns a JSON response with a server error message and a 500 status code
            for unexpected server issues.
        - Returns a 405 status code for requests using a method other than POST.
    """
    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            email = data.get('email')

            if not email:
                return JsonResponse({m:EmptyFields})
            
            try: 
                validate_email(email)
            except ValidationError:
                return JsonResponse({m:EmailNotValid})

            e = EmailAlertForUpcomingProduct.objects.create(
                email = email
            )
# TODO add other field in here how the fuck you gonna know which user enrolled from where ?
            if not e:
                return JsonResponse({m:'ServerErorr'}, status=500)
            return JsonResponse(SUCCESS_TRUE)
        except Exception as er:
            print(ErrorBar , '\n' , er)
            return JsonResponse({m:ServerErorr} , status=500)
    return JsonResponse({m:MethodNotAllowed} , status=405)

def supportPage(r):
    """
    Renders the support page.

    This function is a view that handles requests for the support page. It takes
    a request object `r` and uses Django's `render` shortcut to display the
    'support.html' template. This is a simple view that doesn't require any
    context data to be passed to the template.

    Args:
        r: The HTTP request object.

    Returns:
        An HttpResponse object that renders the 'support.html' template.
    """
    return render(r, 'support.html')


def checkoutPage(r):
    return render(r, 'checkout.html')

address_validation_setting:dict = {'allow_empty_phone' : False , 'check_pincode' : True , 'check_phone' : True  , 'required_fields' : ['fname' , 'lname' , 'address' , 'city' , 'state' , 'pincode' , 'phone' , 'flat']}

def validate_address_payload(payload:dict , agree:bool) -> tuple:
    """
    Validate address payload (pure function). Returns (cleaned_dict, errors_dict).
    Cleaned values are safe to assign (strings trimmed & escaped).
    """
    if not agree:
        errors['notaggree'] = 'Please agree to the terms and conditions'
        return errors , cleaned
    
    errors:dict = {}
    cleaned:dict = {}
    to_validate = address_validation_setting.get('required_fields')
    def _check_fields(name):
        """
    Checks if a field exists and is not empty.

    This function retrieves a value from the `payload` dictionary based on the
    given field name. It strips any leading or trailing whitespace and
    then checks if the resulting string is empty. If the field is empty or
    does not exist, it adds a `FieldRequired` error to the `errors`
    dictionary and returns False. Otherwise, it returns True.
    Args:
        name (str): The name of the field to check.
    Returns:
            bool: True if the field is valid (exists and is not empty), False otherwise.
        """
        val = (payload.get(name) or '').strip()
        if not val:
            errors[name] = FieldRequired
            return False
        return True

    for f in to_validate:
        if f == 'phone' and address_validation_setting['allow_empty_phone']:
            continue
        djk = _check_fields(f)
        if not djk:
            return errors , cleaned #exit as soon as first emty field is found not need to check furthor 
        
    def _trim(name, maxlen):
        val = (payload.get(name) or '').strip()
        if val and len(val) > maxlen:
            errors[name] = f"Maximum length is {maxlen} characters."
        # escape to avoid any accidental HTML injection back into templates/DB
        return escape(val)
    cleaned['shipping_first_name'] = _trim('fname', 50)
    cleaned['shipping_last_name'] = _trim('lname', 50)
    cleaned['shipping_address_1'] = _trim('address', 255)
    cleaned['shipping_address_2'] = _trim('flat', 255)
    cleaned['shipping_city'] = _trim('city', 50)
    cleaned['shipping_state'] = _trim('state', 50)
    cleaned['shipping_zip_code'] = _trim('pincode', 10)
    cleaned['shipping_landmark'] = _trim('landmark', 250)
    cleaned['shipping_note'] = _trim('note', 1000)  
    cleaned['shipping_house_no'] = _trim('flat', 100)  
        # Phone validation
    if address_validation_setting.get('check_phone'):
        phone = (payload.get('phone') or '').strip()
        if phone:
            if not PHONE_RE.match(phone):
                errors['phone'] = "Phone number looks invalid. Use digits, optional leading +."
            else:
                cleaned['shipping_number'] = phone
        else:
            cleaned['shipping_number'] = ''

    # checkbox indicating this is the shipping address (checked => "on")
    cleaned['agree'] = agree
    return errors,cleaned

def cartpricecalculator(prices:list, ShippingPrice:int , discount:int) -> list:
    """
    Helper Function to calculate order pricing.
    
    Args:
        prices (list): list of di   cts, each with 'price' and 'qty'
        shipping (int): flat shipping charge
        discount (int): discount amount (flat, not %)

    Returns:
        dict with subtotal, discount, shipping, tax, final
        or error message
    """

    subtotal:int = 0

    for o in prices:
        if o.get('qty') is None:
            return [False , 'qty is zero' ]
        subtotal += Decimal(str(o.get('price'))) * Decimal(str(o.get('qty')))
    print(subtotal)
    
    if subtotal <= 0:
        return [False , 'Subtotal is cant be Zero']
    
    discount = min(Decimal(str(discount)), subtotal)    

    taxable_amount = ( subtotal - discount )  + ShippingPrice

    tax_amount = (taxable_amount * Decimal('18')) / Decimal('100')

    tax_amount = tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    final = (subtotal - discount) + Decimal(str(ShippingPrice)) + tax_amount



    if final > MinimamOrderPrice:  #<------------- minimam price that should be in the final
        return [True , subtotal , tax_amount , final , discount , taxable_amount]
    else:
        return [False , 'Minimum order price is 100.']




@login_required
def addresspage(request):
    """
    Show address page for the current user (GET) and accept address form (POST).
    - Uses request.user.cart_items.
    - Returns template with 'message' (products list) and 'shipping' (user shipping data).
    - Validates and saves POSTed address data to request.user fields.
    - Simple rate-limiter protects the POST endpoint.
    """
    user = request.user 
    price:list = []

    # flags
    is_address = user.is_s_a

    if request.method == 'POST':
        cache_key = f'address_post_attempts:{user.pk}'
        attempts = cache.get(cache_key , 0) # <-- return zero if no previus post request
        if attempts >=  address_prpu:
            logger.warning("Too many address POST attempts for user_id=%s", user.pk)
            return JsonResponse({m:ToManyattempts})
        try:
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)
            is_changed = data.get('changed', False)
            if is_changed:
                e,c = validate_address_payload(data.get('address' , {}) , data.get('Agree' , False)) 
                if e:
                    return JsonResponse(e)
                user.shipping_first_name = c.get("shipping_first_name", "")
                user.shipping_last_name = c.get("shipping_last_name", "")
                user.shipping_address_1 = c.get("shipping_address_1", "")
                user.shipping_address_2 = c.get("shipping_address_2", "")
                user.shipping_city = c.get("shipping_city", "")
                user.shipping_state = c.get("shipping_state", "")
                user.shipping_zip_code = c.get("shipping_zip_code", "")
                user.shipping_landmark = c.get("shipping_landmark", "")
                user.shipping_note = c.get("shipping_note", "")
                user.shipping_number = c.get("shipping_number", "")
                user.terms_conditions = bool(c.get("agree", False))
                user.shipping_house_no = c.get('shipping_house_no' , '')
                user.is_s_a = True
                try:
                    user.save(update_fields=[
                        "shipping_first_name", "shipping_last_name", "shipping_address_1",
                        "shipping_address_2", "shipping_city", "shipping_state",
                        "shipping_zip_code", "shipping_landmark", "shipping_note",
                        "shipping_number", "terms_conditions" , 'shipping_house_no', 'is_s_a'
                    ])
                except (DatabaseError, IntegrityError, ValidationError) as e:
                    logger.exception(f"{e} \n Failed to save shipping info for user %s", user.pk)
                    return JsonResponse({"ok": False, "error-code": 'shadd-01'}, status=500)
                return JsonResponse({'message' : 'Your address has been saved , please wait' , 'redirect' : 'checkout/'} , status=201)
            else:
                return JsonResponse({'message' : "The address above will be used for shipping." , 'redirect' : 'checkout/'} , )
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON format.'}, status=400)
        except ValidationError:
            return JsonResponse({m: 'There is nothing we can do!'})
        
        

    cart_items = request.user.cart_items.all().select_related()
    pf:list = []
    for items in cart_items:
        pn = items.product
        pd =PRODUCT_INFO.get(pn)
        product_price_qty = {'price' : pd.get('price'), 'qty': items.quantity or None}
        price.append(product_price_qty)
        print(price)
        pd['name'] = pn
        pd['qty'] = items.quantity
        pf.append(pd)
    Discount = 10  #<--------- should get from database
    uc = cartpricecalculator(price , ShippingPrice , Discount)
    print( ErrorBar,'\n' , uc)
    context:dict = {'message' : pf , 'uc' : uc} 

    raw:dict = {'user cart' : pf , 'discount' : Discount}

    if is_address == True:
        shipping_initial = {
            'fname': user.shipping_first_name or '',
            'lname': user.shipping_last_name or '',
            'flat': user.shipping_house_no or '',
            'address': user.shipping_address_1 or '',
            'city': user.shipping_city or '',
            'state': user.shipping_state or '',
            'pincode': user.shipping_zip_code or '',
            'landmark': user.shipping_landmark or '',
            'phone': user.shipping_number or '',
            'same': 'on' if default else '',
        }

        context = {"message" : pf , "shipping" : shipping_initial , 'uc' : uc}

    errors:dict = {}
    success_message = None

    return render(request, 'address.html' , context=context)