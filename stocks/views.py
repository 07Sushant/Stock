from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# # Create your views here.
import requests

from .models import Stocks, UserInfo, UserStock
import threading

webscoket_api_key = 'd1hqgb1r01qsvr2bqhc0d1hqgb1r01qsvr2bqhcg'
#

# def fun(request) :
#     page  = '''
#     <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <title>Title</title>
# </head>
# <body>
# <h1>Stock Market App</h1>
# <p>Lorem ipsum dolor sit amet, consectetur adipisicing elit. Blanditiis commodi dignissimos dolor, ducimus enim harum in ipsum iure laboriosam minus, natus odit officiis omnis optio quibusdam quo, sapiente sunt voluptatibus!</p>
# <ul>
#     <li>s1</li>
#     <li>s2</li>
#     <li>s3</li>
# </ul>
# </body>
# </html>
#     '''
#     return  HttpResponse(page)

@login_required
def index(request):
    user = request.user
    user_stocks = UserStock.objects.select_related('stock').filter(user=user)

    total_value = 0
    invested = 0

    for item in user_stocks:
        stock_value = item.purchase_quantity * item.stock.curr_price
        invested_value = item.purchase_quantity * item.purchase_price

        total_value += stock_value
        invested += invested_value
        item.total_value = stock_value
        
        # Calculate individual stock gain/loss
        item.gain_loss = stock_value - invested_value
        item.gain_loss_percentage = ((stock_value - invested_value) / invested_value) * 100 if invested_value != 0 else 0

    gains = ((total_value - invested) / invested) * 100 if invested != 0 else 0

    context = {
        'data': user_stocks,
        'total_value': total_value,
        'invested': invested,
        'gains': round(gains, 2),
    }

    return render(request, 'index.html', context)

def getData(request) :
    nasdaq_tickers = [
        "AAPL",  # Apple Inc.
        "MSFT",  # Microsoft Corporation
        "GOOGL",  # Alphabet Inc. (Class A)
        "GOOG",  # Alphabet Inc. (Class C)
        "AMZN",  # Amazon.com Inc.
        "META",  # Meta Platforms Inc.
        "NVDA",  # NVIDIA Corporation
        "TSLA",  # Tesla Inc.
        "PEP",  # PepsiCo Inc.
        "INTC",  # Intel Corporation
        "CSCO",  # Cisco Systems Inc.
        "ADBE",  # Adobe Inc.
        "CMCSA",  # Comcast Corporation
        "AVGO",  # Broadcom Inc.
        "COST",  # Costco Wholesale Corporation
        "TMUS",  # T-Mobile US Inc.
        "TXN",  # Texas Instruments Inc.
        "AMGN",  # Amgen Inc.
        "QCOM",  # Qualcomm Incorporated
        "INTU",  # Intuit Inc.
        "PYPL",  # PayPal Holdings Inc.
        "BKNG",  # Booking Holdings Inc.
        "GILD",  # Gilead Sciences Inc.
        "SBUX",  # Starbucks Corporation
        "MU",  # Micron Technology Inc.
        "ADP",  # Automatic Data Processing Inc.
        "MDLZ",  # Mondelez International Inc.
        "ISRG",  # Intuitive Surgical Inc.
        "ADI",  # Analog Devices Inc.
        "MAR",  # Marriott International Inc.
        "LRCX",  # Lam Research Corporation
        "REGN",  # Regeneron Pharmaceuticals Inc.
        "ATVI",  # Activision Blizzard Inc.
        "ILMN",  # Illumina Inc.
        "WDAY",  # Workday Inc.
        "SNPS",  # Synopsys Inc.
        "ASML",  # ASML Holding N.V.
        "EBAY",  # eBay Inc.
        "ROST",  # Ross Stores Inc.
        "CTAS",  # Cintas Corporation
        "BIIB",  # Biogen Inc.
        "MELI",  # MercadoLibre Inc.
        "ORLY",  # O'Reilly Automotive Inc.
        "VRTX",  # Vertex Pharmaceuticals Inc.
        "DLTR",  # Dollar Tree Inc.
        "KHC",  # The Kraft Heinz Company
        "EXC",  # Exelon Corporation
        "FAST",  # Fastenal Company
        "JD",  # JD.com Inc.
        "CRWD"  # CrowdStrike Holdings Inc.
    ]

    headers = {
        'Content-Type': 'application/json'
    }
    token  =  "fced443141e501d554d0b38c4a34bba085172b1e"
    def getStock(ticker):
        url  = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={token}"
        priceurl  =  f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"
        requestResponse = requests.get(url, headers=headers )
        Metadata  = requestResponse.json()
        print(Metadata)
        priceData  = requests.get(priceurl , headers=headers)
        print(priceData.json())
        priceData =  priceData.json()[0]['close']

        # insert into SQL
        stock = Stocks(ticker  = Metadata['ticker']  , name  =  Metadata['name'] ,  description =  Metadata['description'] , curr_price  = priceData)
        stock.save()

    nasdaq_tickers =  nasdaq_tickers[11:30]
    for i in nasdaq_tickers :
        getStock(i)


    return HttpResponse("Stock Data Downloaded")


@login_required
def stocks(request):
    # Check if stocks exist, if not, populate them
    if not Stocks.objects.exists():
        try:
            # Populate stocks automatically
            nasdaq_tickers = [
                "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA", "PEP", "INTC",
                "CSCO", "ADBE", "CMCSA", "AVGO", "COST", "TMUS", "TXN", "AMGN", "QCOM", "INTU"
            ]
            
            headers = {'Content-Type': 'application/json'}
            token = "fced443141e501d554d0b38c4a34bba085172b1e"
            
            for ticker in nasdaq_tickers[:10]:  # Limit to first 10 to avoid API rate limits
                try:
                    url = f"https://api.tiingo.com/tiingo/daily/{ticker}?token={token}"
                    priceurl = f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?token={token}"
                    
                    metadata_response = requests.get(url, headers=headers)
                    price_response = requests.get(priceurl, headers=headers)
                    
                    if metadata_response.status_code == 200 and price_response.status_code == 200:
                        metadata = metadata_response.json()
                        price_data = price_response.json()
                        
                        if price_data:
                            stock = Stocks(
                                ticker=metadata['ticker'],
                                name=metadata['name'],
                                description=metadata['description'],
                                curr_price=price_data[0]['close']
                            )
                            stock.save()
                except Exception as e:
                    print(f"Error fetching {ticker}: {e}")
                    continue
        except Exception as e:
            print(f"Error populating stocks: {e}")
    
    q = request.GET.get('q')
    if q:
        stock_list = Stocks.objects.filter(name__icontains=q)
    else:
        stock_list = Stocks.objects.all()

    paginator = Paginator(stock_list, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'data': page_obj,
    }
    return render(request, 'market.html', context)


def loginView(request):
    if request.user.is_authenticated:
        return redirect('stocks')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'login.html')
        
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next', 'stocks')
                return redirect(next_url)
            else:
                messages.error(request, "Your account has been disabled.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html')


def logoutView(request) :
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name  =  request.POST.get('first_name')
        last_name  = request.POST.get('last_name')

        address =   request.POST.get('address')
        panCard = request.POST.get('panCard')
        phoneNumber = request.POST.get('phoneNumber')
        profile_pic = request.FILES.get('profile_pic')
        panCard_Image = request.FILES.get('panCard_Image')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'register.html')


        user = User(username=username, email=email , first_name = first_name ,  last_name = last_name)
        user.set_password(password)
        user.save()


        user_info = UserInfo(
            user=user,
            pancard_number =panCard,
            address = address ,
            phone_number=phoneNumber,
            user_image=profile_pic,
            pancard_image=panCard_Image,
        )
        user_info.save()

        login(request, user)

        t1 = threading.Thread(
            target=send_email_async,
            kwargs={
                "subject": " Registration sucessfull",
                "message": f"Dear {user,username} welcome to our platfrom ",
                "from_email": None,
                "recipient_list": [user.email],
            }
        )
        t1.start()

        return redirect('index')

    return render(request, 'register.html')



@login_required
def buy(request , id) :
    stock  = get_object_or_404(Stocks ,  id =  id)
    user =  request.user
    purchase_quantity = int(request.POST.get('quantity'))
    purchase_price =   float(request.POST.get('real-time-price'))
    print(purchase_price)


    # UserStock is an exmaple of Composite Keys in DBMS (user , stock) --> candidate key
    userStocks = UserStock.objects.filter(stock  =  stock   ,  user  =  user).first()
    if userStocks :
        userStocks.purchase_price = (userStocks.purchase_quantity*userStocks.purchase_price  +  purchase_price*purchase_quantity) / (purchase_quantity + userStocks.purchase_quantity)
        userStocks.purchase_quantity =  userStocks.purchase_quantity +  purchase_quantity
        userStocks.save()
    else  :
        userStock = UserStock(stock  = stock ,  user = user  ,  purchase_price =  purchase_price ,  purchase_quantity =  purchase_quantity )
        userStock.save()



    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Buy Option executed successfully",
            "message": f"Your purchase of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [user.email],
        }
    )
    t1.start()
    return redirect('index')



def  sell(request , id) :
    stock = get_object_or_404(Stocks, id=id)
    user = request.user
    sell_quantity = int(request.POST.get('quantity'))
    userStock  =  UserStock.objects.filter(stock  =  stock ,  user =  user).first()

    if userStock.purchase_quantity <  sell_quantity :
        messages.error(request, "Can't sell more than you own")
        return redirect('market')

    userStock.purchase_quantity -= sell_quantity
    userStock.save()
    t1 = threading.Thread(
        target=send_email_async,
        kwargs={
            "subject": "Sell Option executed successfully",
            "message": f"Your sale of stock {stock.name} was successful",
            "from_email": None,
            "recipient_list": [user.email],
        }
    )
    t1.start()

    return redirect('index')




def send_email_async(subject  ,  message  ,  from_email , recipient_list ) :
    send_mail(subject  =  subject ,  message =  message ,  from_email= from_email , recipient_list = recipient_list )

def landing(request):
    return render(request, 'landing.html')
