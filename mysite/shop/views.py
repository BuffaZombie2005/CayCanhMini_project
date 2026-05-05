"""
Views cho website bán cây cảnh.
Kiến trúc: MVC - Models (models.py), Views (views.py), Controllers tương ứng.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from decimal import Decimal
import json

from .models import Product, Category, Cart, CartItem, Order, OrderItem, UserProfile
from .forms import RegisterForm, ProductForm, CategoryForm, CheckoutForm
from .cart import get_or_create_cart
from .decorators import admin_required, login_required_customer
from .llm_chat import chat_with_local_llm
from .chat_catalog import prepare_catalog_for_chat


# ---------- Public Views ----------

CHAT_BOT_SYSTEM_PROMPT_VI = (
    'Bạn là trợ lý của cửa hàng online "Cây Cảnh Xanh". '
    'Chỉ được gợi ý sản phẩm nằm trong phần danh sách "DANH SÁCH SẢN PHẨM ĐANG CÓ" '
    'trong system message; không bịa tên, giá hay link nếu không có trong danh sách. '
    'Khi gợi ý hãy nêu tên, giá (VNĐ), tồn kho/ngắn gọn có còn hàng không, và đường dẫn '
    'dạng /products/…/ khớp từng dòng trong danh sách. '
    'Nếu không có hàng phù hợp thì nói thẳng và gợi ý thử trang "Sản phẩm" hoặc từ khóa khác. '
    'Trả lời ngắn gọn, thân thiện bằng tiếng Việt khi khách nhắn tiếng Việt. '
    'Đơn hàng, giao hàng, trang chức năng: nhắc xem Giỏ hàng / Đơn hàng hoặc footer (hotline, email)—không đoán sai.'
)


def chat_assistant(request):
    """Trang chat bot (LLM cục bộ qua Ollama)."""
    return render(request, 'shop/chat.html', {
        'llm_model': getattr(settings, 'LLM_MODEL', 'llama3.2'),
    })


@require_POST
def chat_assistant_send(request):
    """API nhận JSON { "message": "...", "history": [ optional Ollama messages ] }."""
    max_len = 4000
    max_turns = 12
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON không hợp lệ.'}, status=400)

    user_text = (payload.get('message') or '').strip()
    if not user_text:
        return JsonResponse({'error': 'Vui lòng nhập tin nhắn.'}, status=400)
    if len(user_text) > max_len:
        return JsonResponse({'error': f'Tin nhắn quá dài (tối đa {max_len} ký tự).'}, status=400)

    history = payload.get('history')
    history_user_texts = []
    if isinstance(history, list):
        for item in history[-max_turns * 2:]:
            if not isinstance(item, dict):
                continue
            role = item.get('role')
            content = (item.get('content') or '').strip()
            if role == 'user' and content:
                history_user_texts.append(content)

    catalog_text, suggested_products = prepare_catalog_for_chat(
        request,
        user_text,
        tuple(history_user_texts[-6:]),
    )
    system_content = (
        CHAT_BOT_SYSTEM_PROMPT_VI
        + '\n\nDANH SÁCH SẢN PHẨM ĐANG CÓ (chỉ gợi ý từ đây):\n'
        + catalog_text
    )
    messages = [{'role': 'system', 'content': system_content}]

    if isinstance(history, list):
        for item in history[-max_turns * 2:]:
            if not isinstance(item, dict):
                continue
            role = item.get('role')
            content = (item.get('content') or '').strip()
            if role not in ('user', 'assistant') or not content:
                continue
            if len(content) > max_len:
                continue
            messages.append({'role': role, 'content': content})

    messages.append({'role': 'user', 'content': user_text})

    reply, err = chat_with_local_llm(messages)
    if err:
        return JsonResponse({'error': err}, status=502)
    return JsonResponse({
        'reply': reply,
        'suggested_products': suggested_products,
    })


def home(request):
    """Trang chủ - sản phẩm nổi bật."""
    products = Product.objects.filter(status='active')[:8]
    categories = Category.objects.all()[:6]
    return render(request, 'shop/home.html', {
        'products': products,
        'categories': categories,
    })


def product_list(request):
    """Danh sách sản phẩm - Search, Filter, Sort."""
    qs = Product.objects.filter(status='active').select_related('category')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    # Filter by category
    cat = request.GET.get('category', '')
    if cat:
        qs = qs.filter(category__slug=cat)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            qs = qs.filter(price__gte=Decimal(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=Decimal(max_price))
        except (ValueError, TypeError):
            pass

    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        qs = qs.order_by('price')
    elif sort == 'price_desc':
        qs = qs.order_by('-price')
    elif sort == 'name':
        qs = qs.order_by('name')
    else:
        qs = qs.order_by('-created_at')

    categories = Category.objects.all()
    return render(request, 'shop/product_list.html', {
        'products': qs,
        'categories': categories,
        'search_q': q,
        'filter_category': cat,
        'sort': sort,
    })


def product_detail(request, slug):
    """Chi tiết sản phẩm."""
    product = get_object_or_404(Product, slug=slug, status='active')
    return render(request, 'shop/product_detail.html', {'product': product})


# ---------- Cart ----------

@require_POST
def add_to_cart(request, product_id):
    """Thêm sản phẩm vào giỏ."""
    if not request.user.is_authenticated:
        next_url = request.META.get('HTTP_REFERER') or reverse('shop:product_list')
        register_url = f"{reverse('shop:register')}?next={next_url}"
        messages.warning(request, 'Vui lòng đăng ký hoặc đăng nhập trước khi thêm sản phẩm vào giỏ.')
        return redirect(register_url)

    product = get_object_or_404(Product, pk=product_id, status='active')
    if not product.in_stock:
        messages.error(request, 'Sản phẩm đã hết hàng.')
        return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))

    quantity = int(request.POST.get('quantity', 1))
    quantity = max(1, min(quantity, product.stock))

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity = min(item.quantity + quantity, product.stock)
        item.save()

    messages.success(request, f'Đã thêm "{product.name}" vào giỏ hàng.')
    return redirect(request.META.get('HTTP_REFERER', 'shop:cart'))


def cart_view(request):
    """Xem giỏ hàng."""
    cart = get_or_create_cart(request)
    return render(request, 'shop/cart.html', {'cart': cart})


@require_POST
def update_cart_item(request, item_id):
    """Cập nhật số lượng."""
    item = get_object_or_404(CartItem, pk=item_id, cart=get_or_create_cart(request))
    quantity = int(request.POST.get('quantity', 1))
    quantity = max(1, min(quantity, item.product.stock))
    item.quantity = quantity
    item.save()
    messages.success(request, 'Đã cập nhật giỏ hàng.')
    return redirect('shop:cart')


@require_POST
def remove_cart_item(request, item_id):
    """Xóa khỏi giỏ."""
    item = get_object_or_404(CartItem, pk=item_id, cart=get_or_create_cart(request))
    item.delete()
    messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    return redirect('shop:cart')


# ---------- Checkout & Orders ----------

@login_required_customer
def checkout(request):
    """Đặt hàng - yêu cầu đăng nhập."""
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Giỏ hàng trống.')
        return redirect('shop:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                shipping_address=form.cleaned_data['shipping_address'],
                shipping_phone=form.cleaned_data['shipping_phone'],
                note=form.cleaned_data.get('note', ''),
                total_amount=cart.get_total(),
                status='pending',
            )
            for ci in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=ci.product,
                    product_name=ci.product.name,
                    price=ci.product.price,
                    quantity=ci.quantity,
                    subtotal=ci.subtotal,
                )
                ci.product.stock -= ci.quantity
                ci.product.save()
            cart.items.all().delete()
            messages.success(request, f'Đặt hàng thành công! Mã đơn: {str(order.id)[:8]}')
            return redirect('shop:order_detail', order_id=str(order.id))
    else:
        profile = getattr(request.user, 'profile', None)
        initial = {}
        if profile and profile.address:
            initial['shipping_address'] = profile.address
        if profile and profile.phone:
            initial['shipping_phone'] = profile.phone
        form = CheckoutForm(initial=initial)

    return render(request, 'shop/checkout.html', {'cart': cart, 'form': form})


@login_required
def order_list(request):
    """Danh sách đơn hàng của user."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """Chi tiết đơn hàng."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


# ---------- Auth ----------

def register_view(request):
    """Đăng ký tài khoản."""
    if request.user.is_authenticated:
        return redirect('shop:home')
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('shop:home')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse('shop:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'user'})
            login(request, user)
            messages.success(request, 'Đăng ký thành công! Chào mừng bạn.')
            return redirect(next_url)
        else:
            for field, errs in form.errors.items():
                for e in errs:
                    messages.error(request, e)
    else:
        form = RegisterForm()
    return render(request, 'shop/register.html', {'form': form, 'next': next_url})


class CustomLoginView(LoginView):
    template_name = 'shop/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    messages.success(request, 'Bạn đã đăng xuất.')
    return redirect('shop:home')


# ---------- Admin Views ----------

@admin_required
def dashboard(request):
    """Dashboard admin - thống kê, biểu đồ."""
    from django.utils import timezone
    from datetime import timedelta

    # Dữ liệu cho Chart.js
    last_7_days = [timezone.now().date() - timedelta(days=i) for i in range(6, -1, -1)]
    orders_by_day = []
    for d in last_7_days:
        count = Order.objects.filter(created_at__date=d, status__in=['confirmed', 'shipped', 'delivered']).count()
        orders_by_day.append(count)

    # Top categories
    from django.db.models import Count
    top_cats = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')[:5]
    cat_labels = [c.name for c in top_cats]
    cat_counts = [c.product_count for c in top_cats]

    stats = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'total_revenue': Order.objects.filter(
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(s=Sum('total_amount'))['s'] or 0,
    }

    import json
    return render(request, 'shop/admin/dashboard.html', {
        'stats': stats,
        'chart_days': json.dumps([d.strftime('%d/%m') for d in last_7_days]),
        'chart_orders': json.dumps(orders_by_day),
        'chart_cat_labels': json.dumps(cat_labels),
        'chart_cat_counts': json.dumps(cat_counts),
    })


@admin_required
def product_admin_list(request):
    """Admin - danh sách sản phẩm (CRUD)."""
    products = Product.objects.all().select_related('category')
    # Search
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    # Filter status
    status = request.GET.get('status', '')
    if status:
        products = products.filter(status=status)
    # Sort
    sort = request.GET.get('sort', '-created_at')
    products = products.order_by(sort)
    return render(request, 'shop/admin/product_list.html', {'products': products, 'search_q': q, 'filter_status': status})


@admin_required
def product_admin_create(request):
    """Admin - thêm sản phẩm."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm sản phẩm.')
            return redirect('shop:product_admin_list')
        for errs in form.errors.values():
            for e in errs:
                messages.error(request, e)
    else:
        form = ProductForm()
    return render(request, 'shop/admin/product_form.html', {'form': form, 'title': 'Thêm sản phẩm'})


@admin_required
def product_admin_edit(request, pk):
    """Admin - sửa sản phẩm."""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật sản phẩm.')
            return redirect('shop:product_admin_list')
        for errs in form.errors.values():
            for e in errs:
                messages.error(request, e)
    else:
        form = ProductForm(instance=product)
    return render(request, 'shop/admin/product_form.html', {'form': form, 'product': product, 'title': 'Sửa sản phẩm'})


@admin_required
@require_POST
def product_admin_delete(request, pk):
    """Admin - xóa sản phẩm."""
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, 'Đã xóa sản phẩm.')
    return redirect('shop:product_admin_list')


@admin_required
def category_admin_list(request):
    """Admin - danh sách danh mục."""
    categories = Category.objects.annotate(product_count=Count('products'))
    return render(request, 'shop/admin/category_list.html', {'categories': categories})


@admin_required
def category_admin_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã thêm danh mục.')
            return redirect('shop:category_admin_list')
        for errs in form.errors.values():
            for e in errs:
                messages.error(request, e)
    else:
        form = CategoryForm()
    return render(request, 'shop/admin/category_form.html', {'form': form, 'title': 'Thêm danh mục'})


@admin_required
def category_admin_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật danh mục.')
            return redirect('shop:category_admin_list')
        for errs in form.errors.values():
            for e in errs:
                messages.error(request, e)
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'shop/admin/category_form.html', {'form': form, 'category': cat, 'title': 'Sửa danh mục'})


@admin_required
@require_POST
def category_admin_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    cat.delete()
    messages.success(request, 'Đã xóa danh mục.')
    return redirect('shop:category_admin_list')


@admin_required
def order_admin_list(request):
    """Admin - quản lý đơn hàng."""
    orders = Order.objects.all().select_related('user').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'shop/admin/order_list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'order_status_choices': Order.STATUS_CHOICES,
    })


@admin_required
def order_admin_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        from .forms import OrderStatusForm
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật trạng thái đơn hàng.')
            return redirect('shop:order_admin_detail', order_id=str(order.id))
    else:
        from .forms import OrderStatusForm
        form = OrderStatusForm(instance=order)
    return render(request, 'shop/admin/order_detail.html', {'order': order, 'form': form})
