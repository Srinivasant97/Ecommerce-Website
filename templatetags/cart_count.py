from django import template
from products.models import Order


register = template.Library()

@register.filter
def cart_count(user):
    if user.is_authenticated:
        Co=Order.objects.filter(user=user, ordered=False)
        if Co.exists():
            return Co[0].items.count()

@register.filter
def modulo(num, val):
    return num % val == 0