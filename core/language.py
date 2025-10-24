"""
================================================================================
language.py
================================================================================

__summary__:
    Centralized string storage for messages used across the entire project.
    its also stores allowed strings and paths

__description__:
    This module defines reusable static strings such as success messages, 
    error prompts, alerts, and labels. It helps maintain consistency in 
    communication across templates, views, and forms.

    Import this module wherever text messages are required instead of hardcoding
    them, to improve maintainability and translation-readiness in the future.

__usage__:
    from .language import FORM_SUCCESS, ERROR_MISSING_FIELDS

__author__:
    Hivefusion lab team

__created__:
    July 2025

"""

# The following list contains the specific URLs (paths) that are tracked
# by the user activity logger.
# 
# To log more pages, simply add the new path string to this list.
# For example, to track a 'blog' page, add '/blog/' to the list.
#
# IMPORTANT: Only the paths in this list will be logged. If a path is
# not included, user visits to that page will not be recorded.

#change this if you want to log more pages ! other then this
TRACKABLE_PATHS = [
    '/', 
    '/about/', 
    '/products/', 
    '/contact/',
    '/login/',
    '/register/',
]


# LOGO_PATH = os.path.join(BASE_DIR, 'static/images/white-hivefusion-log.svg')
# with open(LOGO_PATH, 'rb') as f:
#     HIVEFUSION_LOGO_BYTES = f.read()



#<----------------- Product codes & Prices---------------------->

ShippingPrice:int = 50 #<-------- change this accordingly if the labs works (Lets see if i need to change it in the futur )

# The minimum total price required to place an order.
# You can change this value to adjust the minimum order price.
# For example, to set the minimum price to $50, change the number to 50.
# MinumamOrderPrice is in integer

MinimamOrderPrice:int = 100 

PRODUCTS:dict = {
    '2223' : 'Hivefusion labs Console',
    '2194' : 'Hivefusion labs Pocket Mini'
}


# WARNING: Changing any values in this dictionary will directly affect the product
# display on the website's frontend. This could lead to a 'disaster,' such as incorrect
# prices, broken image links, or non-functional product pages.
# Only modify this if you are absolutely sure of the changes and have tested them.

PRODUCT_INFO = {
    "Hivefusion labs Console": {
        "price": 159,
        "image_url": "/static/images/hifefusion-lab-console-front-with-cable.png",
        "url": "/product/hivefusion-lab-console/"
    },
    "Hivefusion labs Pocket Mini": {
        "price": 249,
        "image_url": "/static/images/hivefusion-lab-pocket-mini-white-background-0x0b.png",
        "url": "/product/hivefusion-lab-pocket-mini/"
    },
}

#<-----------Time Delay and all ------------ > 

TokenExpiry:int = 30 #in minutes
"""
The duration, in minutes, for which a password reset token is valid.

This integer variable specifies the time a password reset token will remain active
before it expires, ensuring a secure and time-sensitive process for password recovery.
"""

#<---------------- Rate limiters-------------->
address_prpu:int = 20
"""post request per user for address uploading is set to be 20"""

#<-------------Messages-------------->#
contectyou:str = "we will contact you soon!"
m:str = "message"   

#<-------------errors---------------->

NameToBig:str = 'Name is too long.'
EmptyFields:str = 'Please fill out all fields.'
ServerErorr:str = 'Internel server error'
EmailAlreadyExists:str = 'Email is already registered.'
WeakPassword:str = 'Password must be at least 8 characters.'
PasswordDoesNotMatch = 'Password does not match.'
EpicResponse_1:str = 'Itna Sannata Kyun Hai Bhai?'
QtyIsNone :str = 'quantity Can not be less then 1'
MethodNotAllowed:str = 'Method Not Allowed !'
EmailNotValid:str = 'Bhai email , EMAIL please' 
ToManyattempts:str = 'Too many requests'
FieldRequired :str = "This field is required."
#<------------succsess------------->

SUCCESS_TRUE:dict = {'success' : True}

#<-----------Console---------------->

ErrorBar = """
##################################################
#                     ERROR                      #
##################################################
"""

testBar:str = """
##################################################
#                     TEST                       #
##################################################
"""