import random
from datetime import datetime
from decimal import Decimal

from django import template
from django.db.models.aggregates import Sum

register = template.Library()


@register.filter(name='date')
def timestamp_to_date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%d-%m-%y")


@register.filter(name='unit_name')
def unit_name(breakdown):
    if breakdown.product.name.startswith('LSL'):
        return 'Pcs.'
    return 'Cup'


@register.filter(name='vat_reference')
def vat_reference(remarks):
    return remarks.split(';;;')[0]


@register.filter(name='vat_amount')
def vat_amount(remarks):
    parts = remarks.split(';;;')
    return ('%.02f' % float(parts[1]) if len(parts) > 1 else 0)


@register.filter(name='grand_total')
def grand_total(order):
    total = order.breakdown.all().aggregate(Sum('total'))['total__sum']
    parts = order.remarks.split(';;;')
    if len(parts) > 0:
        try:
            total += Decimal(parts[1])
        except:
            pass
    return ('Tk. %.02f' % total)


@register.filter(name='get_random')
def get_random(start, end):
    return random.randint(start, end)
