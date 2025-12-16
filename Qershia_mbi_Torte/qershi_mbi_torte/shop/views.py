from .models import Product,Order,OrderItem,Favorite,UserProfile
from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings



def home(request):
    return render(request, 'shop/home.html')

def about_us(request):
    context = {
        'text': """
Mirësevini në Pasticeri “Qershia mbi Tortë”  
Çdo ditë përgatisim ëmbëlsira dhe torta të freskëta, me përkushtim dhe dashuri, për t’i bërë momentet tuaja të veçanta edhe më të ëmbla.  

Historia jonë nisi me pasionin për ëmbëlsirat artizanale dhe dëshirën për të sjellë diçka ndryshe në tryezat e klientëve tanë. Duke përdorur përbërës të freskët dhe me cilësi të lartë, ne krijojmë torta unike, të përshtatura për çdo rast – nga festat familjare te eventet më të rëndësishme.  

Në ambientet tona moderne dhe mikpritëse, do të gjeni një gamë të gjerë produktesh, ku tradita dhe inovacioni bashkohen për të ofruar shije që mbeten gjatë në kujtesë.  

“Qershia mbi Tortë” është simboli i ëmbëlsisë, cilësisë dhe kujtimeve të bukura. Jemi këtu për t’ju shoqëruar në çdo moment të veçantë të jetës suaj!
        """
    }
    return render(request, 'shop/about_us.html', context)


def product_list(request):
    sort_by = request.GET.get('sort_by', 'name')
    allowed_sort_fields = ['name', '-name', 'price', '-price']
    if sort_by not in allowed_sort_fields:
        sort_by = '-name'
    products = Product.objects.all().order_by(sort_by)
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
    else:
        user_favorites = []
    return render(request, 'shop/product_list.html', {
        'products': products,
        'user_favorites': user_favorites
    })

def contact_us(request):
        context = {
            'tiktok_link': 'https://www.tiktok.com/@qershi_mbi_torte?_t=8hlPuDSy8TV&_r=1&fbclid=PAdGRleAOuZrNleHRuA2FlbQIxMQBzcnRjBmFwcF9pZA8xMjQwMjQ1NzQyODc0MTQAAaeUYd2zREA_aGLRboIHaqUbc0GXv7A6IlhEsENeni_MYGn53Qj7yIcPFuWQhQ_aem_GXfwFwCAofXMT2WEc8XOKw',
            'instagram_link': 'https://www.instagram.com/qershi_mbi_torte/',
        }
        return render(request, 'shop/contact_us.html', context)


def register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ky username ekziston tashmë.')
            return render(request, 'shop/login.html')

        if password != confirm_password:
            messages.error(request, 'Fjalëkalimet nuk përputhen.')
            return render(request, 'shop/login.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(user=user, address=address, phone_number=phone_number)

        messages.success(request, 'Llogaria u krijua me sukses! Tani mund të kyçeni.')
        return redirect('client_login')

    return render(request, 'shop/login.html')

def client_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You are now logged in!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "shop/login.html")

def client_logout(request):
    logout(request)
    messages.success(request, "You are now logged out.")
    return redirect('home')

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        quantity = item['quantity']
        price = item['price']
        total += price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
        })

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, "shop/cart.html", context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    product_id_str = str(product.id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image_url': product.image.url if product.image else None
        }

    request.session['cart'] = cart
    total_items = sum(item['quantity'] for item in cart.values())
    request.session['cart_total_items'] = total_items
    return redirect('cart')

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    if str(product.id) in cart:
        product_id_str = str(product.id)
        action = request.GET.get('action')

        if action == 'add':
            cart[product_id_str]['quantity'] += 1
        elif action == 'remove':
            if cart[product_id_str]['quantity'] > 1:
                cart[product_id_str]['quantity'] -= 1
            else:
                del cart[product_id_str]

        request.session['cart'] = cart
        total = sum(item["price"] * item["quantity"] for item in cart.values())

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "quantity": cart.get(product_id_str, {}).get("quantity", 0),
                "total": total,
            })

    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    if str(product.id) in cart:
        del cart[str(product.id)]
        request.session['cart'] = cart
        messages.success(request, f"Produkti '{product.name}' u hoq nga shporta.")
    return redirect('cart')

@login_required
def create_order_from_cart(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Shporta është bosh.")
        return redirect('cart')

    order = Order.objects.create(user=request.user, status='pending')

    for product_id, item in cart.items():
        product = get_object_or_404(Product, id=product_id)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
        )
    request.session['cart'] = {}
    return redirect('checkout', order_id=order.id)


@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method")

        if payment_method == "bank":
            # Shfaq faqen e bankës
            return render(request, "shop/bank_payment.html", {"order": order})

        elif payment_method == "cash":
            order.payment_method = "cash"
            order.status = "confirmed"
            order.save()

            send_order_email(order) 
            return render(request, "shop/success.html", {"order": order})

        else:
            messages.error(request, "Ju lutem zgjidhni një mënyrë pagese.")
            return redirect("checkout", order.id)

    return render(request, "shop/checkout.html", {"order": order})


@login_required
def cart_checkout(request):
    cart_items = request.session.get('cart', {})
    if not cart_items:
        return redirect('cart')  # shporta bosh
    order = Order.objects.create(customer=request.user, status='pending')
    for item_id, details in cart_items.items():
        OrderItem.objects.create(
            order=order,
            product_id=item_id,
            quantity=details['quantity'],
            price=details['price']
        )
    return redirect('checkout', order_id=order.id)


@login_required
def success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, "shop/success.html", {"order": order})


def product_search(request):
    q = request.GET.get("q", "")
    products = Product.objects.filter(name__icontains=q) if q else Product.objects.all()
    return render(request, "shop/search.html", {"products": products, "q": q})

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
    return redirect("favorite_list")

@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "shop/favorites.html", {"favorites": favorites})


def send_order_email(order):
    items = order.items.all()

    product_lines = []
    for item in items:
        product_lines.append(
            f"- {item.product.name} x {item.quantity} = {item.subtotal()} ALL"
        )

    subject = f"Porosi e re #{order.id}"
    message = f"""
Ka ardhur një porosi e re!

Klienti: {order.user.username}
Email: {order.user.email}

Produkte:
{chr(10).join(product_lines)}

Totali: {order.total_price()} ALL
Mënyra e pagesës: {order.get_payment_method_display()}
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['qershiaambitortee@gmail.com'],
        fail_silently=False,
    )
    
from django.core.mail import send_mail
from django.conf import settings

def test_email(request):
    send_mail(
        'TEST SMTP',
        'Ky është një test nga Django',
        settings.DEFAULT_FROM_EMAIL,
        ['qershiaambitortee@gmail.com'],
        fail_silently=False,
    )
    return HttpResponse("Email u dërgua")
