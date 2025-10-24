import json
import threading
import os
import uuid
from django.shortcuts import render , HttpResponse, redirect
from accounts.models import CustomUser,CartItem
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import authenticate , login
from core.language import m,ServerErorr,EmailAlreadyExists,WeakPassword,EmptyFields,PasswordDoesNotMatch,ErrorBar,EpicResponse_1,PRODUCTS,QtyIsNone,SUCCESS_TRUE,MethodNotAllowed,PRODUCT_INFO,testBar, TokenExpiry
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.cache import cache
from datetime import datetime, timedelta

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
import logging
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect

# TODO -> implement a cart reminder feature such that when the user add something to there cart the webiste will send them  a email to remind them with some greed

logger = logging.getLogger(__name__)

token_generator = PasswordResetTokenGenerator()


def generate_verification_link(request, user):
    """
    Generate a secure email verification URL for the given user.

    Args:
        request (HttpRequest): Current request object (needed for absolute URL)
        user (User): Django user instance (must have a PK)

    Returns:
        str | None: Absolute verification URL or None if generation fails
    """
    try:
        if not user or not getattr(user, 'pk', None):
            logger.error("Verification link generation failed: invalid user object.")
            return None

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        verification_path = reverse('verify_email', kwargs={
            'uidb64': uidb64,
            'token': token
        })

        verification_link = request.build_absolute_uri(verification_path)
        print(testBar , '\n' , 'generated link --------->  ' , verification_link)
        return verification_link

    except Exception as e:
        logger.exception(f"Error generating verification link: {e}")
        return None


def send_welcome_email(to_email, user_name):
    subject = "Welcome to HiveFusion Lab"
    message = f"Hello {user_name},\n\nWelcome to HiveFusion Lab! We're excited to have you on board.\n\nBest,\nHiveFusion Lab Team"
    
    send_mail(
        subject,
        message,
        'welcome@lab.hivefusion.in',  # From email
        [to_email],                   # Recipient list
        fail_silently=False
    )

def send_welcome_email_html(to_email, user_name, verification_url):
    subject = "Welcome to HiveFusion Lab"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">

        <table align="center" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <tr>
                <td style="background-color: #ff4d4f; padding: 20px; text-align: center;">
                <h2 style="color:white; , font:bold;">Hivefusion Lab </h2>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px; color: #333;">
                    <h2 style="color: #ff4d4f; margin-top: 0;">Hello {user_name},</h2>
                    <p style="font-size: 16px; line-height: 1.6;">
                        Welcome to <strong>HiveFusion Lab</strong>! 🎉<br>
                        We're thrilled to have you on board.
                    </p>
                    <p style="font-size: 16px; line-height: 1.6;">
                        Please verify your email to complete your registration.
                    </p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" style="background-color: #ff4d4f; color: white; padding: 12px 24px; text-decoration: none; font-size: 16px; border-radius: 6px; display: inline-block;">
                            Verify Email
                        </a>
                    </div>

                    <p style="font-size: 14px; color: #777;">
                        If you didn’t create an account, you can safely ignore this email.
                    </p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #888;">
                    &copy; {2025} HiveFusion Lab. All rights reserved.
                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, "", 'welcome@lab.hivefusion.in', [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def forgot_password_email(to_email , user_name , link) -> None:
    subject = "Welcome to HiveFusion Lab"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f6f6f6; padding: 20px;">

        <table align="center" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <tr>
                <td style="background-color: #ff4d4f; padding: 20px; text-align: center;">
                <h2 style="color:white; , font:bold;">Hivefusion Lab </h2>
                </td>
            </tr>
            <tr>
                <td style="padding: 30px; color: #333;">
                    <h2 style="color: #ff4d4f; margin-top: 0;">Hello {user_name},</h2>
                    <p style="font-size: 16px; line-height: 1.6;">
                        We received a request to reset your password for your <strong>HiveFusion Lab</strong> account.
                    </p>
                    <p style="font-size: 16px; line-height: 1.6;">
                        Click the button below to set a new password:
                    </p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{link}" style="background-color: #ff4d4f; color: white; padding: 12px 24px; text-decoration: none; font-size: 16px; border-radius: 6px; display: inline-block;">
                            Reset Password
                        </a>
                    </div>

                    <p style="font-size: 14px; color: #777;">
                        If you didn’t request a password reset, you can safely ignore this email. 
                        Your password will remain unchanged.
                    </p>
                </td>
            </tr>
            <tr>
                <td style="background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #888;">
                    &copy; {2025} HiveFusion Lab. All rights reserved.
                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, "", 'welcome@lab.hivefusion.in', [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_welcome_email_async(to_email, user_name , link):
    threading.Thread(
        target=send_welcome_email_html,
        args=(to_email, user_name , link),
        daemon=True
    ).start()

def send_forgot_password_email_async(to_email, user_name:str , link:str) -> None : 
    threading.Thread(
        target=forgot_password_email,
        args=(to_email , user_name , link),
        daemon=True
    ).start()

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user.is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect('/')


    if user is not None and token_generator.check_token(user, token):
        user.is_verified = True
        user.save()
        messages.success(request, "Your email has been verified successfully.")
        return redirect('/')
    else:
        messages.error(request, "Verification link is invalid or expired.")
        return redirect('/')

def signup(request):
    if request.method == "POST":
        try:
            
            body_unicode = request.body.decode('utf-8')
            data = json.loads(body_unicode)

            uname = data.get('name')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirm_password')

            print('user data => ' , uname,  email , password , confirm_password , len(password) )

            if not email or not password or not confirm_password or not uname:
                return JsonResponse({m: EmptyFields}, status=400)
            if not len(password) >= 8:
                return JsonResponse({m: WeakPassword}, status=400)
            if password != confirm_password:
                return JsonResponse({m: PasswordDoesNotMatch}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({m: EmailAlreadyExists}, status=409)
                    
            try:
                user = CustomUser.objects.create_user(
                first_name=uname,
                username=email,
                email=email,
                password=password,
                status='New_customer',
                last_visit=timezone.now()
                )
            except Exception as usercreate:
                print(ErrorBar , '\n' , usercreate)
                return JsonResponse({m: ServerErorr})
            
            link = generate_verification_link(request, user)
            if not link:
                return JsonResponse({m:'idk bro , link cant be generated!'})
            send_welcome_email_async(email, uname , link)
            login(request , user)
            return JsonResponse({'success': True, 'redirect_url': '/'}) 

        except Exception as e:
            print(ErrorBar , '\n' , e)
            return JsonResponse(ServerErorr, status=500)
    return render(request , 'sign_up.html')

def loginpage(request):
    """
    Handles user login requests.

    This view processes both GET and POST requests for the login page.
    
    If the request method is **POST**:
        - It attempts to authenticate the user using the provided email and password.
        - If authentication is successful, the user is logged in and redirected to the homepage ('/').
        - If authentication fails, or if the email or password fields are empty, an error message is
        displayed on the login page.

    If the request method is **GET**:
        - It simply renders the login page without any authentication attempt.

    Args:
        request (HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse: Renders the login page with an optional error message, or
                    redirects to the homepage upon successful login.
    """
    if request.method == "POST":
        data = request.POST
        Email = data.get('email')
        Password = data.get('password')
        
        if not Email or not Password:
            return render(request, 'login.html', {'error': 'Please enter both email and password.'})
        
        user = authenticate(request, username=Email, password=Password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid email or password.'})
    
    return render(request, 'login.html')


def forgotPasswordPage(r):
    """
    Handles the forgot password request by sending a password reset link to the user's email.

    This function processes POST requests containing a user's email address. It validates the
    email, checks if a user exists with that email, generates a unique token, and creates a
    password reset link. The link and token data are then stored in a cache with a specific
    timeout. An asynchronous email is sent to the user with the reset link.

    Args:
        r (HttpRequest): The Django HttpRequest object.

    Returns:
        HttpResponse: A Django HttpResponse object that renders the 'sunil.html' template.
        It includes a success message if the email is sent, or an error
        message if the email is not found or is missing from the request.
    """
    if r.method == 'POST':
        data = r.POST
        Email = data.get('email')

        if not Email:
            return render(r , 'sunil.html' , {'error' : EmptyFields})
        
        user = CustomUser.objects.filter(email=Email).first()

        if not user:
            return render(r , 'sunil.html' , {'error' : 'No user found with that email.'})
        token = str(uuid.uuid4())
        link = f'127.0.0.1:8000/change-password/{token}'
        # send_forgot_password_email_async(Email , user.first_name , link)
        
        sunil = {
            'email' : Email,
            'token' : token,
            'time' : datetime.utcnow().isoformat()
        }
        cache_key = f"reset:{Email}"
        cache.set(cache_key , sunil , timeout=TokenExpiry * 60)

        return render(r , 'sunil.html' , {'success' : 'A link has been sent your email'})


    return render(r, 'sunil.html')


def forgotpaasswordverification(r):
    pass

@login_required
def UserAddToCart(r):
    if r.method == "POST":
        try:
            body_unicode = r.body.decode('utf-8')
            data = json.loads(body_unicode)
            p_code = data.get('p_code')
            quantity = data.get('qty')
            
            try:
                quantity = int(quantity)
            except ValueError:
                return JsonResponse({'message': 'Quantity must be an integer.'}, status=400)
            
            if not p_code or not quantity:
                return JsonResponse({m:EpicResponse_1})

            if quantity < 1 :
                return JsonResponse({m:QtyIsNone})
            
            product_name = PRODUCTS.get(p_code)
            
            if not product_name:
                return JsonResponse({'message': 'Product code not valid.'}, status=400)
                
            cart_item , created = CartItem.objects.get_or_create(
                user=r.user,
                product=product_name,
                defaults={'quantity' : quantity},
            )
            if not created :
                cart_item.quantity += quantity
                cart_item.save()

            if r.user.status != 'CART':
                r.user.status = 'CART'
                r.user.save(update_fields=['status'])

            product_list = r.user.product_in_cart or []
            if product_name not in product_list:
                product_list.append(product_name)
                r.user.product_in_cart = product_list
                r.user.save(update_fields=['product_in_cart'])

            history = r.user.purchase_dates or []
        
            history.append({
                "type": "cart-update",
                "time": timezone.now().isoformat()  # ISO format for easy parsing
            })
            r.user.purchase_dates = history
            r.user.save(update_fields=['purchase_dates'])
            return JsonResponse(SUCCESS_TRUE)

        except Exception as e:
            print(ErrorBar , '\n' , e)
            return JsonResponse({m: ServerErorr} , status=500)
    return JsonResponse({m:MethodNotAllowed})


def check_login(request):
    """
    Checks if the user is authenticated.

    This view function returns a JSON response indicating the authentication status
    of the current user. It's a simple utility endpoint that can be used by
    front-end JavaScript to determine if the user is logged in without a full
    page reload.

    Args:
        request: The HTTP request object.

    Returns:
        A JsonResponse containing a dictionary with a single key 'ls' (for login status)
        whose value is a boolean indicating whether the user is authenticated.
    """
    return JsonResponse({'ls': request.user.is_authenticated})


@login_required
def get_user_cart(request):
    """
    Retrieves the authenticated user's shopping cart contents.

    This view handles a POST request to fetch all items currently in the user's
    shopping cart from the database. It then enriches the cart data with additional
    product information (like price and image URL) from a predefined dictionary.

    Args:
        request (HttpRequest): The HTTP request object. Expected to be a POST request.
                            The user must be authenticated.

    Returns:
        JsonResponse: A JSON response containing the cart data.
                    - If the cart is empty, returns a 204 No Content status with a message.
                    - If successful, returns a 200 OK status with a list of cart items.
        
    Raises:
        HttpResponseNotAllowed: If the request method is not POST.
    """
    if request.method == "POST":
        items = CartItem.objects.filter(user=request.user)
        data = []

        if not items.exists():
            return JsonResponse({'data': [], 'message': 'Cart is empty'}, status=204)
        for item in items:
            product_name = item.product
            product_info = PRODUCT_INFO.get(product_name)

            if product_info:
                data.append({
                "product": product_name,
                "qty": item.quantity,
                "price": product_info["price"],
                "image_url": product_info["image_url"],
                "product_url": product_info["url"],
                })
            else:
                data.append({
                    "product": product_name,
                    "qty": item.quantity,
                    "price": None,
                    "image_url": None,
                    "product_url": None,
                })
        return JsonResponse({'data' : data })

    return JsonResponse({m:MethodNotAllowed})

def profilepage(r):
    return JsonResponse({m : 'we are still developing'})


