from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic import ListView,DetailView
from .models import Item,OrderItem,Order,BillingAddress,Payment
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckoutForm
import stripe
stripe.api_key = ""
#API key stored in env 
# Create your views here.
class Checkout(ListView):
    def get(self,*args,**kwargs):
        form = CheckoutForm()
        context={
            'form' : form
        }
        return render(self.request,"checkout.html",context)
    def post(self,*args,**kwargs):
        form=CheckoutForm(self.request.POST or None)
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                street_name=form.cleaned_data.get('street_name')
                apartment_no=form.cleaned_data.get('apartment_no')
                country=form.cleaned_data.get('country')
                zip=form.cleaned_data.get('zip')
                payment_option=form.cleaned_data.get('payment_option')
                billing_address=BillingAddress(
                    user=self.request.user,
                    street_name=street_name,
                    apartment_no=apartment_no,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                if payment_option == "S":
                    return redirect('products:payment',option="stripe")
                elif payment_option == "P":
                    return redirect('products:payment',option="paypal")
                
                else:
                    return redirect('products:checkout')
                
            messages.warning(self.request,"Failed Checkout")
            return redirect('products:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request,"You do not have an active order")
            return redirect("products:order_summary")

class Home(ListView):
    model=Item
    paginate_by=4
    template_name="home.html"
class Product(DetailView):
    model=Item
    template_name="product.html"

@login_required(login_url='/login/')
def add_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_item,created=OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"The quantity is updated.")
        else:
            order.items.add(order_item)
            messages.info(request,"The quantity is added ")
    else:
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"The quantity is added")
    
    return redirect("products:product",slug=slug)

@login_required(login_url='/login/')
def remove_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]

            order.items.remove(order_item)  
            messages.info(request,"Item Removed Successfully")
        else:
            messages.info(request,"Item not in the Cart")
    
    else:
        messages.info(request,"No Order Found")

    return redirect("products:product",slug=slug)

class Register(FormView):
	form_class = UserCreationForm
	template_name = 'registration/register.html'
	redirect_authenticated_user=True
	success_url= reverse_lazy('products:home')

	def form_valid(self,form):
		user=form.save()
		if user is not None:
			login(self.request,user)
		return super(Register,self).form_valid(form)
	def get(self,*args, **kwargs):
		if self.request.user.is_authenticated:
			return redirect('home')
		return super(Register,self).get(*args, **kwargs)

class OrderSummary(LoginRequiredMixin,ListView):
    login_url = '/login/'
    def get(self,*args,**kwargs):
        try:
            order=Order.objects.get(user=self.request.user,ordered=False)
            context={
                "object":order
            }
            return render(self.request,"order_summary.html",context)
        except ObjectDoesNotExist:
            return redirect("/")



def add_one_item_to_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_item,created=OrderItem.objects.get_or_create(item=item,user=request.user,ordered=False)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity+=1
            order_item.save()
    else:
        ordered_date=timezone.now()
        order=Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        order_item.quantity=1
    
    return redirect("products:order_summary")

def remove_one_item_from_cart(request,slug):
    item=get_object_or_404(Item,slug=slug)
    order_qs=Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order=order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item=OrderItem.objects.filter(item=item,user=request.user,ordered=False)[0]
            if order_item.quantity>1:
                order_item.quantity -=1
            else:
                order.items.remove(order_item) 
            order_item.save()
        
    


    return redirect("products:order_summary")


class PaymentView(ListView):
    def get(self,*args,**kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        context={
            'order':order
        }
        return render(self.request,"payment.html",context)
    
    def post(self,*args,**kwargs):
        order=Order.objects.get(user=self.request.user,ordered=False)
        token=self.request.POST.get('stripeToken')
        amount=int(order.total())
        try:
            charge=stripe.Charge.create(
                amount=amount,
                currency="INR",
                source=token
            )
            payment=Payment(
                stripe_charge_id=charge['id'],
                user=self.request.user,
                amount=order.total(),
                timestamp=timezone.now()
            )
            payment.save()
            order.ordered=True
            order.payment=payment
            order.save()
            messages.success(self.request,"Your Transaction was Successful")
            return redirect("/")
        except stripe.error.CardError as e:
            messages.error(self.request, e.get('message'))
            return redirect("/")
        except stripe.error.RateLimitError:
            messages.error(self.request,"Rate Limit Error")
            return redirect("/")
        except stripe.error.InvalidRequestError as a:
            messages.error(self.request,"Invalid Request")
            return redirect("/")
        except stripe.error.AuthenticationError:
            messages.error(self.request,"Not Authenticated")
            return redirect("/")
        except stripe.error.APIConnectionError:
            messages.error(self.request,"Network Error")
            return redirect("/")
        except stripe.error.StripeError:
            messages.error(self.request,"Error Occured. Try again Later")
            return redirect("/")
        except Exception as e:
            messages.error(self.request,"We are working on this issue")
            return redirect("/")
