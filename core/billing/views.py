from django.shortcuts import render
from django.http import JsonResponse
from .forms import AddItem, UpdateItem
from .models import Order, Item
import re

# Create your views here.


def index(request):
    form = AddItem()
    new_order = Order.objects.create()
    context = {"form": form,
               "new_order": new_order}
    return render(request, 'billing/index.html', context)


def search_item(request):
    item_name = request.GET.get('item-name')
    query = re.compile(item_name, re.IGNORECASE)
    suggestions = []
    for item in Item.objects.all():
        if re.search(query, item.name):
            suggestions.append((item.name, item.id))
    # context = {"suggestions": suggestions}
    return JsonResponse(suggestions, safe=False)


def add_item(request):
    pass
