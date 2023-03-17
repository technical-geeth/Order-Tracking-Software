import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
from .models import Order, Item, OrderItem
from .context_processors import new_order_id
from .utils import delete_order_item
from .receipt_printer import print_receipt
import re
from django.conf import settings


#  logging setup
LOG_DIR = settings.BASE_DIR / 'logs'
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': f'{LOG_DIR}/debug.log'
        }
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file']
        }
    }
})


logger = logging.getLogger(__name__)

#  Views


def index(request):
    order_id = new_order_id(request).get('new_order_id')
    order = Order.objects.get_or_create(pk=order_id)
    context = {'order': order}
    return render(request, 'index.html', context)


@csrf_exempt
def search_items(request):
    logger.debug('Function Name: search_items')
    item_name = request.POST.get('item-name')
    suggestions = []
    try:
        index_number = int(item_name)
        item = Item.objects.get(pk=index_number)
        suggestions.append(
            (item, str(item))
        )
    except ValueError:
        query = re.compile(item_name, re.IGNORECASE)

        for item in Item.objects.all():
            if re.search(query, item.name):
                suggestions.append(
                    #  item[0] is the item object
                    #  item[1] is the string to represent the item
                    (item, str(item)))
    context = {"suggestions": suggestions}
    return render(
        request,
        'partials/search-results.html',
        context
    )


@csrf_exempt
def add_item(request, item_id):
    logger.debug('Function Name: add_item')
    #  adds item to the order
    order_id = new_order_id(request).get('new_order_id')
    logger.debug(f"Received order_id: {order_id}")
    item = Item.objects.get(pk=item_id)
    order = Order.objects.get_or_create(pk=order_id)[0]
    if item in order.items.all():
        logger.debug(f'Item {item.name} already in order {order_id}')
        order_item = order.orderitem_set.get(item__pk=item_id)
        order_item.quantity += 1
        order_item.save()
        logger.info(
            f'Updated order_item {order_item.item.name} for order {order_item.order.id}')
        context = {"order": order,
                   'message': f'Item already in order. Updated Quantity to {order_item.quantity}'}
        return render(
            request,
            'partials/show-added-items.html',
            context
        )
    logger.debug(f'Received item {item.name}')
    if item in order.items.all():
        logger.debug(f'Item {item.name} already in order {order_id}')
        order_item = order.orderitem_set.get(item__pk=item_id)
        order_item.quantity += 1
        order_item.save()
        logger.info(
            f'Updated order_item {order_item.item.name} for order {order_item.order.id}')
        context = {"order": order,
                   'message': f'Item already in order. Updated Quantity to {order_item.quantity}'}
        return render(
            request,
            'partials/show-added-items.html',
            context
        )
    logger.debug(f'Received item {item.name}')
    order_item = OrderItem.objects.create(
        order=order,
        item=item)
    order_item.save()
    logger.info(
        f'Created order_item {order_item.item.name} for order {order_item.order.id}')
    context = {"order": order}
    return render(
        request,
        'partials/show-added-items.html',
        context
    )


@csrf_exempt
def update_item_quantity(request, item_id, order_id):
    logger.debug('Function Name: update_item_quantity')
    # updates the quantity of the item in the order
    quantity = request.POST.get('item-quantity')
    order = Order.objects.get(pk=order_id)
    logger.debug(f'Got order: {order}')
    order_item = order.orderitem_set.get(item__pk=item_id)
    logger.debug(f'Got relative order_item: {str(order_item.item)}')
    order_item.quantity = quantity
    logger.debug(f'Updated quantity: {order_item.quantity}')
    order_item.save()
    context = {"order": order}
    return render(request, 'partials/show-added-items.html', context)


@csrf_exempt
def delete_item(request, order_id, item_id):
    logger.debug('Function Name: delete_item')
    order = delete_order_item(order_id, item_id)
    context = {
        'order': order
    }
    return render(request,
                  'partials/show-added-items.html', context)


@csrf_exempt
def create_order(request, order_id):
    logger.debug('Function Name: create_order')
    logger.debug(f'Created Order {order_id}')
    order = Order.objects.get(pk=order_id)
    order.is_new = False
    order.save()
    logger.info(f'Saved order {order_id}')
    new_order = Order.objects.create(pk=order_id+1)
    logger.debug(f'Created new order {order_id+1}')
    context = {
        'prev_order': order,
        'order': new_order,
    }
    return render(request, 'index.html', context)


@csrf_exempt
def update_table_number(request, order_id):
    logger.debug('Function Name: update_table_number')
    logger.info(f'Updating table number for order {order_id}')
    order = Order.objects.get(pk=order_id)
    logger.debug(f'Got order {order.id}')
    table_number = request.POST.get('table-number')
    logger.debug(f'Got table number {table_number}')
    old_table_number = order.table_number
    order.table_number = table_number
    order.save()
    logger.info(
        f'Updated table number for order {order.id} from {old_table_number} to {order.table_number}'
    )
    logger.debug(
        f'Updated table number in Order {order.id} is {order.table_number}')

    context = {
        'order': order,
    }
    return render(request, 'index.html', context)


# @csrf_exempt
def modal_view(request, order_id):
    logger.debug('Function: modal_view')
    order = Order.objects.get(pk=order_id)
    logger.debug(f'Got order: {order.id} Reqeuested Order: {order_id}')
    context = {
        'order': order,
        'order_id': order.id,
    }
    return render(request, 'modal.html', context)


@csrf_exempt
def print_receipt_view(request, order_id):
    logger.debug('Function: print_receipt_view')
    order = Order.objects.get(pk=order_id)
    logger.debug('Function: print_receipt_view')
    print_receipt(order)
    context = {
        'order': order,
    }
    return render(request, 'partials/modal-recent-order.html')
