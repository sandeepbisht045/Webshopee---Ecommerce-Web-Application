from django.shortcuts import render,redirect
from .models import Product, Contact, Order, OrderUpdate,Customer
from math import ceil
import json
from django.http import HttpResponse

# function for index---------------------------------------------------------------------------------------------
def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    # print(request.session.get("email"))
    return render(request, 'shop/index.html', params)

# for about us page----------------------------------------------------------------------------------------------
def about(request):
    return render(request, 'shop/about.html')

# function for contact page-----------------------------------------------------------------------------------------
def contact(request):
    if request.method=="POST":
        if request.session.get("customer_id"):
            name = request.POST.get('name', '')
            email = request.POST.get('email', '')
            phone = request.POST.get('phone', '')
            desc = request.POST.get('desc', '')
            contact = Contact(name=name, email=email, phone=phone, desc=desc)
            contact.save()
        else:
            return render(request,"shop/login.html")
    return render(request, 'shop/contact.html')

# function for tracking----------------------------------------------------------------------------------------
def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        print(orderId,email)
        try:
            order = Order.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json] ,default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')
    # return render(request,"shop/tracker.html")
    else:
        return render(request, "shop/tracker.html")

# for search template------------------------------------------------------------------------------------------------
def search(request):

    return render(request, 'shop/search.html')


def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})

# function for checkout-------------------------------------------------------------------------------
def checkout(request):
    if request.method=="POST":
        if request.session.get("customer_id"):
            cust_email=request.session.get("email")
            items_json = request.POST.get('itemsJson', '')
            name = request.POST.get('name', '')
            amount = request.POST.get('amount', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get('phone', '')
            order = Order(items_json=items_json, name=name, email=email, address=address, city=city,
                           state=state, zip_code=zip_code, phone=phone,amount=amount,cust_details=cust_email)
            order.save()
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()
            thank = True
            id = order.order_id
            return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
        else:
            return render(request,"shop/login.html")
    return render(request, 'shop/checkout.html')

# function for search functionality---------------------------------------------------------------
def search(request):
    query= request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query, item)]
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!= 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg":""}
    if len(allProds)==0 or len(query)<4:
        params={'msg':"Enter a valid Search"}
    return render(request, 'shop/search.html', params)


def searchMatch(query, item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

# function for signup---------------------------------------------------------------------------------------
def signup(request):
    flag=""
    if request.method=="POST":
        pdata=request.POST.get
        fname=pdata("firstname")
        lname=pdata("lastname")
        email=pdata("email")
        phone=pdata("phone")
        password1=pdata("password1")
        password2=pdata("password2")

        form=Customer.objects.all()
        for i in form:
            if i.email==email or i.phone==phone:
                flag=True
        if flag:
            alert="user already exist"
        elif not flag:
            if password1!= password2:
                alert="password doesnot match"
            else:
                Customer(firstname=fname,lastname=lname,email=email,phone=phone,password=password1,prepeat=password2).save()
                alert="Registration Successful"

        return render(request,"shop/signup.html",{"alert":alert ,"first_name":fname,"last_name":lname,"email":email,"phone":phone})
    else:

        return render(request,"shop/signup.html")


# function for login---------------------------------------------------------------------------------
def login(request):
    form=""
    flag=""
    if request.method=="POST":
        pdata = request.POST.get

        credential = pdata("text")
        password1 = pdata("password1")
        form = Customer.objects.all()
        for i in form:
            if (i.email==credential or i.phone==credential) and password1==i.password:
                flag=True
                cid=i.id
                cemail=i.email
                fname=i.firstname
                lname=i.lastname
                phone=i.phone

        if  flag:
            alert="Login Success"
            print("login success")
            flag=True
            request.session["customer_id"]=cid
            request.session["email"] = cemail
            request.session["fname"] = fname
            request.session["lname"] = lname
            request.session["phone"] = phone

            return redirect( "/shop", {"alert": alert,"flag":flag,"fname":fname})

        else:
                alert="Invalid Credentials"

                return render(request,"shop/login.html",{"alert":alert,"credential":credential})
    else:
        return render(request, "shop/login.html")

# views for logout----------------------------------------------------------------------------------
def logout(request):
    request.session.clear()
    return redirect("/shop/login")

# views for profile________________________________________________________________________________________

def profile(request):
    fname=request.session.get("fname")
    lname=request.session.get("lname")
    email=request.session.get("email")
    phone=request.session.get("phone")
    return render(request,"shop/profile.html",{"fname":fname,"lname":lname,"email":email,"phone":phone})

# views for orders______________________________________________________________________________________________
def orders(request):
    cust_email = request.session.get("email")
    print(cust_email)
    if request.session.get("customer_id"):

        try:
            cust_orders=Order.objects.filter(cust_details=cust_email)
            print(cust_orders)
            if cust_orders:
              data={"order_fetch":cust_orders}
              return render(request,"shop/orders.html",data)
            else:
                return HttpResponse("No Orders Found")
                # return render(request, "shop/orders.html", {"order_fetch":"No Orders Found"})

        except:
            return HttpResponse("No Orders Found")
            # return render(request,"shop/orders.html",{"order_fetch":"No Orders Found"})


# ________________________________________________________________________________
def chatbot(request):
    return render(request,"shop/chatroom.html")