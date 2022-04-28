from django.shortcuts import render,redirect,get_object_or_404,HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.views.generic import TemplateView,View
from django.db.models import Count
from .forms import CartAddProductForm
from django.db.models import Q
import smtplib
import email.message
import razorpay


def mainPage(request):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        model=Products.objects.filter()[:20]
        if request.GET:
            try:
                q = request.GET.get('search')
                if q:
                    prod= Products.objects.filter(Q(title__icontains=q))
                    data = {
                        'pro' : prod
                    }
            except:
                pass
            return render(request,'main.html',data)
        return render(request,'main.html',{'model':model,'z':z})
    else:
        models=Products.objects.all()[::5]
        return render(request,'main.html',{'models':models})
   
def login(request):
    if request.method=="POST":
        try:
            Email=request.POST['Email']
            Password=request.POST["Password"]
            mod=Registeration.objects.get(Email=Email)
            if mod.Password==Password:
                request.session['Email']=Email
                messages.success(request,'done')
                return redirect('main')
            else:
                msg = 'Please Enter Same Password'
                return render(request , 'login.html',{'msg':msg})
        except:
            msg = 'Wrong Email ID !!!'
            return render(request , 'login.html',{'msg':msg})            
    return render(request,'login.html')

def logout(request):
    del request.session['Email']
    print('User logged out successfully')
    return redirect('login')

def category(request):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        model=Category.objects.all()
        mod=Products.objects.all()
        m=Category.objects.get(id=1)
        qs=Products.objects.filter(category=m).count()

        dict_data = {}

        for i in model:
            qs=Products.objects.filter(category=i).count()
            dict_data[i] = qs
        print(dict_data)
        return render(request,'category.html',{'model':model,'qs':qs,'mod':mod,'z':z,'set_data':dict_data})
    else:
        mo=Category.objects.all()
        mode=Products.objects.all()
        m1=Category.objects.get(id=1)
        qs1=Products.objects.filter(category=m1).count()
        return render(request,'category.html',{'model':mo,'qs':qs1,'mod':mode})

def productview(request,title):
    mod=Products.objects.get(title=title)
    model=Products.objects.all()[:]
    print(model)
    return render(request,'single-product.html',{'mod':mod,'model':model})


def categorywise(request,title):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        model=Category.objects.all()
        cat=Category.objects.get(title=title)
        form1 =Products.objects.all().filter(category=cat)
        return render(request,'category.html',{'form1': form1,'model':model,'z':z})
    else:
        model=Category.objects.all()
        cat=Category.objects.get(title=title)
        form1 =Products.objects.all().filter(category=cat)
        return render(request,'category.html',{'form1': form1,'model':model})

class AddtoCartView(TemplateView):
    template_name="addtocart.html"

    def get_context_data(self,**kwargs):
            context=super().get_context_data(**kwargs)
            product_id=self.kwargs['pro_id']
            print(product_id)
            product_obj=Products.objects.get(id=product_id)
            print(product_obj)
            cart_id=self.request.session.get('cart_id', None)
            print(cart_id)
            if cart_id:
                cart_obj=Cart.objects.get(id=cart_id)
                print(cart_obj)
                product_in_cart=cart_obj.cartproduct_set.filter(product=product_obj)
                print(product_in_cart)
                if product_in_cart.exists():
                    cartproduct=product_in_cart.last()
                    cartproduct.quantity+=1
                    cartproduct.subtotal+=product_obj.selling_price
                    cartproduct.save()
                    cart_obj.total+=product_obj.selling_price
                    cart_obj.save()
                else:
                    cartproduct=CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                    cart_obj.total+=product_obj.selling_price
                    cart_obj.save()
            else:
                cart_obj=Cart.objects.create(total=0)
                self.request.session['cart_id']=cart_obj.id
                cartproduct=CartProduct.objects.create(cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price)
                cart_obj.total+=product_obj.selling_price
                cart_obj.save()
            return context

class ManageCartView(View):
    def get(self,request,*args,**kwargs):
        cp_id=self.kwargs["cp_id"]
        action =request.GET.get("action")
        cp_obj=CartProduct.objects.get(id=cp_id)
        cart_obj=cp_obj.cart
        
        if action=="inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action=="dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity==0:
                cp_obj.delete()

        elif action =="rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect ("mycart")

class EmptyCartView(View):
    def get(self,request,*args,**kwargs):
        cart_id=request.session.get("cart_id", None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total=0
            cart.save()
        return redirect("mycart")

def cartview(request):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        cart_id=request.session.get("cart_id", None)
        cart=Cart.objects.get(id=cart_id)
    else:
        return redirect('login')
    return render(request,'cart.html',{'cart':cart,'z':z})

# class MyCartView(TemplateView):
#     template_name="cart.html"
#     def get_context_data(self, **kwargs):
#         context=super().get_context_data(**kwargs)
#         cart_id=self.request.session.get("cart_id",None)
#         if cart_id:
#             cart=Cart.objects.get(id=cart_id)
#         else:
#             cart=None
#         context['cart']=cart

#         return context

def contact(request):
    if request.method=='POST':
        model=Contact()
        model.name=request.POST['name']
        model.email=request.POST['email']
        model.subject=request.POST['subject']
        model.message=request.POST['message']
        model.save()
        return redirect('main')

    return render(request,'contact.html')

def signup(request):
    if request.method=="POST":
        model=Registeration()
        model.Firstname=request.POST['Firstname']
        model.Lastname=request.POST['Lastname']
        model.Mobile=request.POST['Mobile']
        model.Email=request.POST['Email']
        model.City=request.POST['City']
        model.Country=request.POST['Country']
        model.State=request.POST['State']
        model.Password=request.POST['Password']
        model.Pincode=request.POST['Pincode']
        model.Address=request.POST['Address']
        model.save()
        return redirect('login')
    return render(request,'signup.html')

def confirmation(request):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        cart_id=request.session.get("cart_id", None)
        cart=Cart.objects.get(id=cart_id)
          
        razorpay_amount = cart.total*100
        
        C=CartProduct.objects.filter(cart=cart) 
        
        if request.method == "POST":
            client = razorpay.Client(
            auth=("rzp_test_qDwTmKnksUVsaC", "QOr66ZQbsLdNZOmrV4YGX50V"))
            payment = client.order.create({'amount': razorpay_amount, 'currency': 'INR',
                                    'payment_capture': '1'})
            
    # --------------------------------------------------------------
            if cart:
                my_email = "mailtesting681@gmail.com"
                my_pass = "mailtest123@"
                fr_email = user
                
                server = smtplib.SMTP('smtp.gmail.com',587)
                mead_data = ""
                front = """
                <!DOCTYPE html>
                <html>
                    <body>
                        <div>
                            <h2>Name : """ + z.Firstname + """</h2>
                            <h2>Email : """ + user + """</h2>
                            <h2>Order No: """ + str(cart_id) + """</h2>
                        </div>
                        <br>
                        <div>
                            <table border="2">
                                <thead>
                                    <tr>
                                        <th>
                                            Product Name
                                        </th>
                                        <th>
                                            Product Qty
                                        </th>
                                        <th>
                                            Product Price
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>"""
                                
                for i in C:
                    mead_data += """<tr>
                    <td>""" + str(i.product.title) + """ </td>
                    <td>""" + str(i.quantity) + """ </td> 
                    <td>""" + str(i.product.selling_price) + """</td></td>
                    </tr> """
                    
                ended = """<tr>
                <td colspan="2">
                You Have Paid
                </td><td> """ + str(cart.total) + """
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div> 
                        <br>
                        <div>
                            <h3>Thank you for visiting ....</h3>
                        </div>
                    </body>
                </html>
                """
                email_content = front + mead_data + ended
                print(email_content)
                
                msg = email.message.Message()
                msg['Subject'] = 'Your Bill' 
                msg['From'] = my_email
                msg['To'] = fr_email
                password = my_pass
                msg.add_header('Content-Type', 'text/html')
                msg.set_payload(email_content)
                s = smtplib.SMTP('smtp.gmail.com',587)
                s.starttls()
                s.login(msg['From'], password)
                s.sendmail(msg['From'], [msg['To']], msg.as_string())
                print("ordered succssfully")
                return redirect('emptycart')
        
    else:
        return redirect('login')
    return render(request,'confirmation.html',{'cart':cart,'z':z, 'razorpay_amount':razorpay_amount})


# def confirmation_BACKUP(request):
#     if request.session.get('Email'):
#         user=request.session['Email']
#         z=Registeration.objects.get(Email=user)
#         cart_id=request.session.get("cart_id", None)
#         cart=Cart.objects.get(id=cart_id)
        
#     else:
#         return redirect('login')
#     return render(request,'confirmation.html',{'cart':cart,'z':z})


def sendmail(request):
    if request.session.get('Email'):
        user=request.session['Email']
        z=Registeration.objects.get(Email=user)
        cart_id=request.session.get("cart_id", None)
        cart=Cart.objects.get(id=cart_id)
        
        C=CartProduct.objects.filter(cart=cart) 
        if cart:
            my_email = "mailtesting681@gmail.com"
            my_pass = "mailtest123@"
            fr_email = user
            
            server = smtplib.SMTP('smtp.gmail.com',587)
            mead_data = ""
            front = """
            <!DOCTYPE html>
            <html>
                <body>
                    <div>
                        <h2>Name : """ + z.Firstname + """</h2>
                        <h2>Email : """ + user + """</h2>
                        <h2>Order No: """ + str(cart_id) + """</h2>
                    </div>
                    <br>
                    <div>
                        <table border="2">
                            <thead>
                                <tr>
                                    <th>
                                        Product Name
                                    </th>
                                    <th>
                                        Product Qty
                                    </th>
                                    <th>
                                        Product Price
                                    </th>
                                </tr>
                            </thead>
                            <tbody>"""
                            
            for i in C:
                mead_data += """<tr>
                <td>""" + str(i.product.title) + """ </td>
                <td>""" + str(i.quantity) + """ </td> 
                <td>""" + str(i.product.selling_price) + """</td></td>
                </tr> """
                
            ended = """<tr>
            <td colspan="2">
            You Have Paid
            </td><td> """ + str(cart.total) + """
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div> 
                    <br>
                    <div>
                        <h3>Thank you for visiting ....</h3>
                    </div>
                </body>
            </html>
            """
            email_content = front + mead_data + ended
            print(email_content)
            
            msg = email.message.Message()
            msg['Subject'] = 'Your Bill' 
            msg['From'] = my_email
            msg['To'] = fr_email
            password = my_pass
            msg.add_header('Content-Type', 'text/html')
            msg.set_payload(email_content)
            s = smtplib.SMTP('smtp.gmail.com',587)
            s.starttls()
            s.login(msg['From'], password)
            s.sendmail(msg['From'], [msg['To']], msg.as_string())
            return redirect('main')
        
    else:
        return redirect('login')
    return render(request,'confirmation.html',{'cart':cart,'z':z})
    