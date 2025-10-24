"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lab.views import homepage
from lab.views import aboutpage
from lab.views import cartpage
from lab.views import checkoutPage
from lab.views import addresspage
from accounts.views import signup , loginpage , UserAddToCart , check_login, get_user_cart, verify_email , profilepage , forgotPasswordPage
from lab.views import pocketMiniPage , ConsolePage, UserEnroll , supportPage

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name="homepage"),
    path('about/' , aboutpage , name="about"),
    path('cart' , cartpage, name="cart"),
    path('signup', signup , name="signup"),
    path('login', loginpage , name='login'),
    path('product/hivefusion-lab-pocket-mini/', pocketMiniPage , name='pocket_mini_page'),
    path('product/hivefusion-lab-console/', ConsolePage, name='pocket_mini_page'),
    path('product/up-crt', UserAddToCart , name='user_add_to_Cart'),
    path('product/down-crt', get_user_cart , name='get_user_cart'),
    path('f8e7b3a1/' , check_login , name='checklogin'),
    path('join' , UserEnroll , name="userjoin"),
    path('support' , supportPage , name="support-page"),
    path('verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('/profile' , profilepage , name='profile-page'),
    path('reset-password' , forgotPasswordPage , name='forgot-password-page'),
    path('checkout/' , checkoutPage , name='checkoutpage'),
    path('shipping-address' , addresspage , name='address-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)