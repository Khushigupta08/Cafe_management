from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile, MenuItem, Order, OrderItem,Notification

# User Registration
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        role = request.POST['role']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()

        profile = Profile.objects.create(user=user, role=role)
        profile.save()

        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('cafe/login')
    
    return render(request, 'cafe/register.html')

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            profile = Profile.objects.get(user=user)
            if profile.role == 'owner':
                return redirect('owner_dashboard')
            elif profile.role == 'waiter':
                return redirect('waiter_order_form')
            elif profile.role == 'chef':
                return redirect('chef_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'cafe/login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('cafe/login')

# Owner Dashboard
@login_required
def owner_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'owner':
        return redirect('login')

    orders = Order.objects.all()
    menu_items = MenuItem.objects.all()

    open_orders = Order.objects.filter(orderitem__isnull=False).distinct()

    return render(request, 'cafe/owner_dashboard.html', {'orders': orders,'open_orders': open_orders,menu_items:menu_items})

@login_required
def add_menu_item(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'owner':
        return redirect('cafe/menu/add')

    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        MenuItem.objects.create(name=name, price=price)
        return redirect('cafe/menu/add')

    return render(request, 'cafe/add_menu_item.html')

@login_required
def delete_menu_item(request, item_id):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'owner':
        return redirect('cafe/menu')

    menu_item = get_object_or_404(MenuItem, id=item_id)
    if request.method == 'POST':
        menu_item.delete()
        return redirect('cafe/menu')
    return render(request, 'cafe/delete_menu_item.html', {'menu_item': menu_item})

def menupage(request):
    menu_items = MenuItem.objects.all()
    return render(request,'cafe/menu.html',{'menu_items': menu_items})

# Waiter Order Form
@login_required
def waiter_order_form(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'waiter':
        return redirect('login')

    menu_items = MenuItem.objects.all()
    open_orders = Order.objects.all()

    return render(request, 'cafe/waiter_order_form.html', {'menu_items': menu_items,'open_orders':open_orders})

# def submit_order(request):
#     if request.method == 'POST':
#         table_number = request.POST.get('table_number')
#         customer_name = request.POST.get('customer_name')
#         order = Order.objects.create(waiter=request.user, table_number=table_number, customer_name=customer_name)

#         total_amount = 0
#         for item_id in request.POST.getlist('menu_items'):
#             quantity = int(request.POST.get(f'quantity_{item_id}'))
#             menu_item = MenuItem.objects.get(id=item_id)
#             OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
#             total_amount += menu_item.price * quantity

#         order.total_amount = total_amount
#         order.save()

#         return redirect('cafe/waiter_order_form')

def submit_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        menu_items = request.POST.getlist('menu_items')
        quantities = [int(request.POST.get(f'quantity_{item_id}')) for item_id in menu_items]

        if order_id:
            order = Order.objects.get(id=order_id)
        else:
            table_number = request.POST.get('table_number')
            customer_name = request.POST.get('customer_name')
            order = Order.objects.create(waiter=request.user, table_number=table_number, customer_name=customer_name)

        total_amount = order.total_amount
        for item_id, quantity in zip(menu_items, quantities):
            menu_item = MenuItem.objects.get(id=item_id)
            order_item, created = OrderItem.objects.get_or_create(order=order, menu_item=menu_item)
            order_item.quantity += quantity
            order_item.save()
            total_amount += menu_item.price * quantity

        order.total_amount = total_amount
        order.save()

        return redirect('waiter_order_form')
    
@login_required
def generate_bill(request, order_id):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'owner':
        return redirect('login')

    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'cafe/generate_bill.html', {'order': order, 'order_items': order_items}) 


# Chef Dashboard
@login_required
def chef_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'chef':
        return redirect('login')

    orders = Order.objects.filter(orderitem__isnull=False).distinct()
    return render(request, 'cafe/chef_dashboard.html', {'orders': orders})

def complete_order(request, order_id):
    order = Order.objects.get(id=order_id)
    profile = Profile.objects.get(user=request.user)

    # Logic to mark the order as completed
    # Here you can implement your logic to mark the order completed
    # For example, you could add an 'is_completed' field to the Order model

    # Create a notification for the waiter
    if profile.role == 'chef':
        waiters = User.objects.filter(profile__role='waiter')
        for waiter in waiters:
            Notification.objects.create(
                order=order,
                waiter=waiter,
                message=f'Order ID {order.id} has been completed.'
            )

    return redirect('cafe/chef_dashboard')

@login_required
def waiter_notifications(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'waiter':
        return redirect('cafe/login')

    notifications = Notification.objects.filter(waiter=request.user, is_read=False).order_by('-created_at')
    # Mark notifications as read when viewed
    notifications.update(is_read=True)

    return render(request, 'cafe/waiter_notifications.html', {'notifications': notifications})