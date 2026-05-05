"""Chuẩn bị danh mục sản phẩm thật từ DB cho chatbot gợi ý."""
import re
from django.db.models import Q
from django.urls import reverse

from .models import Product

MAX_CATALOG_ITEMS = 40
MAX_MATCH_FOR_CONTEXT = 20
MAX_SUGGESTIONS_UI = 8
MAX_DESC_CHARS = 140


def _tokens(*texts):
    out = []
    seen = set()
    for text in texts:
        if not text or not isinstance(text, str):
            continue
        for raw in re.split(r'[\s,;.!?/\\\-+]+', text.lower()):
            w = raw.strip()
            if len(w) < 2 or w in seen:
                continue
            seen.add(w)
            out.append(w)
            if len(out) >= 48:
                return out
    return out


def _build_name_desc_q(tokens):
    q = Q()
    for t in tokens:
        q |= (
            Q(name__icontains=t)
            | Q(description__icontains=t)
            | Q(category__name__icontains=t)
        )
    return q


def _product_line(p):
    desc = (p.description or '').replace('\n', ' ').strip()
    if len(desc) > MAX_DESC_CHARS:
        desc = desc[: MAX_DESC_CHARS - 1] + '…'
    stock_note = 'còn hàng' if p.in_stock else 'hết/tạm hết'
    return (
        f"- {p.name} | Danh mục: {p.category.name} | Giá: {int(p.price):,}đ | "
        f"Tồn: {p.stock} ({stock_note}) | Link: /products/{p.slug}/ | {desc}"
    )


def serialize_product_for_chat(request, p):
    rel = reverse('shop:product_detail', kwargs={'slug': p.slug})
    return {
        'name': p.name,
        'slug': p.slug,
        'price': int(p.price),
        'category': p.category.name,
        'stock': p.stock,
        'in_stock': p.in_stock,
        'url': request.build_absolute_uri(rel),
    }


def prepare_catalog_for_chat(request, user_message, history_user_texts=()):
    """
    Trả về (catalog_text, suggestions_for_json).
    catalog_text: chuỗi đưa vào system prompt.
    suggestions_for_json: list dict hiển thị thẻ gợi ý (đã có URL tuyệt đối).
    """
    base = Product.objects.filter(status='active').select_related('category')
    if not base.exists():
        return (
            '(Hiện chưa có sản phẩm nào đang mở bán trên cửa hàng.)',
            [],
        )

    texts = tuple(history_user_texts) + (user_message or '',)
    tokens = _tokens(*texts)

    if tokens:
        matched = (
            base.filter(_build_name_desc_q(tokens))
            .distinct()
            .order_by('-created_at')[:MAX_MATCH_FOR_CONTEXT]
        )
        matched_list = list(matched)
    else:
        matched_list = []

    exclude_ids = {p.pk for p in matched_list}
    need = max(0, MAX_CATALOG_ITEMS - len(matched_list))
    filler_qs = base.exclude(pk__in=exclude_ids).order_by('-created_at')[:need]
    filler_list = list(filler_qs)
    catalog_list = matched_list + filler_list

    catalog_text = '\n'.join(_product_line(p) for p in catalog_list)

    if matched_list:
        ui_list = matched_list[:MAX_SUGGESTIONS_UI]
    else:
        ui_list = catalog_list[:MAX_SUGGESTIONS_UI]

    suggestions = [serialize_product_for_chat(request, p) for p in ui_list]
    return catalog_text, suggestions
