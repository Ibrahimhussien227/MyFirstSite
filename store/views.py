from django.contrib import messages
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
import datetime
from .models import *
from .forms import *
from .utlits import cartData, guestOrder


# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = data['form']['total']
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
            phone=data['shipping']['phone'],
        )
    return JsonResponse('Payment complete', safe=False)


@login_required
def product_details(request, pk):
    products = Product.objects.get(pk=pk)
    comments = Comment.objects.filter(product=products).order_by('-pk')
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = request.POST.get('comment')
            comment = Comment.objects.create(product=products, user=request.user, comment=content)
            comment.save()
            return redirect('product_details', pk=pk)
    else:
        comment_form = CommentForm()
    context = {
        'products': products,
        'cartItems': cartItems,
        'order': order,
        'items': items,
        'comments': comments,
        'comment_form': comment_form}
    return render(request, 'store/product_details.html', context)


@login_required
def product_delete(request, pk):
    products = Product.objects.get(id=pk)
    if request.user.is_superuser:
        Product.objects.get(id=pk).delete()
    return redirect('store')


def edit_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        p_form = ProductUpdateForm(request.POST, request.FILES, instance=product)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'The product has been updated')
            return redirect('product_details', pk=pk)
    else:
        p_form = ProductUpdateForm(instance=product)
    context = {
        'p_form': p_form,
        'product': product
    }
    return render(request, 'store/edit_product.html', context)


def add_product(request):
    form = AddProductForm()
    if request.method == 'POST':
        # print('Printing POST:', request.POST)
        form = AddProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store')
    context = {'form': form}
    return render(request, 'store/add_product.html', context)
