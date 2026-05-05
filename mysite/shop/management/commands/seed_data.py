"""
Management command để tạo dữ liệu mẫu (seed data).
Chạy: python manage.py seed_data
"""
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from shop.models import Category, Product, UserProfile, Order, OrderItem

# Namespace cố định để mỗi đơn seed có UUID không đổi giữa các lần chạy
ORDER_SEED_NS = uuid.UUID('01927bcd-0000-7000-8000-000000000001')


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu: categories, products, đơn hàng, admin user'

    def handle(self, *args, **options):
        # Tạo Admin user nếu chưa có
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@caycanh.vn', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        profile, _ = UserProfile.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
        if profile.role != 'admin':
            profile.role = 'admin'
            profile.save()
        if created:
            self.stdout.write(self.style.SUCCESS('Tao user admin (password: admin123)'))
        else:
            self.stdout.write('User admin da ton tai.')

        # User thường để test
        user1, _ = User.objects.get_or_create(
            username='user1',
            defaults={'email': 'user1@test.com'}
        )
        if user1.check_password('admin123') is False:
            user1.set_password('admin123')
            user1.save()
        UserProfile.objects.get_or_create(user=user1, defaults={'role': 'user'})

        # Categories
        categories_data = [
            ('cay-noi-that', 'Cây nội thất', 'Cây cảnh trang trí trong nhà'),
            ('sen-da', 'Sen đá', 'Các loại sen đá dễ chăm sóc'),
            ('xuong-rong', 'Xương rồng', 'Xương rồng mini, trang trí'),
            ('cay-phong-thuy', 'Cây phong thủy', 'Cây mang may mắn'),
        ]
        for slug, name, desc in categories_data:
            Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc})

        # Products - mỗi sản phẩm có URL ảnh riêng (Unsplash)
        products_data = [
            ('lan-y', 'Lan Ý', 'Cây lan ý lọc không khí, dễ chăm', 150000, 20, 'cay-noi-that',
             'https://images.unsplash.com/photo-1765364333787-f33514772885?w=400'),
            ('truc-nhat', 'Trúc Nhật', 'Cây trúc nhật xanh mát', 180000, 15, 'cay-noi-that',
             'https://images.unsplash.com/photo-1643754547206-97f97802b916?w=400'),
            ('monstera-deliciosa', 'Monstera', 'Lá xẻ đặc trưng, trang trí phòng khách', 220000, 18, 'cay-noi-that',
             'https://images.unsplash.com/photo-1520412099551-62b6bafeb5bb?w=400'),
            ('trau-ba', 'Trầu bà', 'Leo dây hoặc thủy canh, tươi tốt', 95000, 35, 'cay-noi-that',
             'https://images.unsplash.com/photo-1593691509543-c55fb32d8de5?w=400'),
            ('luoi-ho', 'Lưỡi hồ', 'Chịu hạn, lọc không khí ban đêm', 125000, 22, 'cay-noi-that',
             'https://images.unsplash.com/photo-1533038590846-1d6a17c82e4c?w=400'),
            ('thiet-moc-lan', 'Thiết mộc lan', 'Hoa thơm, lá dày bóng', 175000, 14, 'cay-noi-that',
             'https://images.unsplash.com/photo-1454263868755-778d8b6c2e12?w=400'),
            ('trau-ba-vang', 'Trầu bà vàng', 'Lá vàng xanh, thân bám', 110000, 28, 'cay-noi-that',
             'https://images.unsplash.com/photo-1592150621744-aca64f48394a?w=400'),
            ('philodendron-xanh', 'Philodendron xanh', 'Lá lớn, bán bóng một phần', 135000, 20, 'cay-noi-that',
             'https://images.unsplash.com/photo-1545241047-6081a3785f12?w=400'),
            ('sen-da-nau', 'Sen đá nâu', 'Sen đá màu nâu đất', 45000, 50, 'sen-da',
             'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400'),
            ('sen-da-xanh', 'Sen đá xanh ngọc', 'Sen đá xanh mướt', 50000, 40, 'sen-da',
             'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400'),
            ('sen-da-tim', 'Sen đá tím', 'Màu tím pastel, thích nắng nhẹ', 55000, 45, 'sen-da',
             'https://images.unsplash.com/photo-1459156212016-c8604681f087?w=400'),
            ('sen-da-hong', 'Sen đá hồng', 'Viền lá hồng, combo chậu nhỏ', 48000, 52, 'sen-da',
             'https://images.unsplash.com/photo-1463937585777-83995fcd3a82?w=400'),
            ('haworthia-mini', 'Haworthia mini', 'Sen đá dạng lá dày trong suốt', 42000, 65, 'sen-da',
             'https://images.unsplash.com/photo-1509587584298-0f3b3a3a1797?w=400'),
            ('echeveria-lola', 'Echeveria Lola', 'Hoa hồng đá, dễ nhân giống', 58000, 38, 'sen-da',
             'https://images.unsplash.com/photo-1520301255226-bf5f991fff6f?w=400'),
            ('sen-da-de', 'Sen đá dê', 'Lá dày tròn, chậu terrarium', 52000, 44, 'sen-da',
             'https://images.unsplash.com/photo-1596547619332-3842c08748d2?w=400'),
            ('sen-da-lai', 'Sen đá lai', 'Màu sắc đa dạng, chậu mix', 46000, 48, 'sen-da',
             'https://images.unsplash.com/photo-1446071103084-c257b5f70672?w=400'),
            ('xuong-rong-cau-vong', 'Xương rồng cầu vồng', 'Xương rồng nhiều màu', 35000, 60, 'xuong-rong',
             'https://images.unsplash.com/photo-1509587584298-0f3b3a3a1797?w=400'),
            ('xuong-rong-tron', 'Xương rồng tròn', 'Thân cầu, ít tưới', 32000, 55, 'xuong-rong',
             'https://images.unsplash.com/photo-1526036494772-36d2f6ef85f7?w=400'),
            ('xuong-rong-cot', 'Xương rồng cột', 'Thân đứng, trang trí góc sáng', 38000, 42, 'xuong-rong',
             'https://images.unsplash.com/photo-1459411552884-841db9b3cc2a?w=400'),
            ('xuong-rong-hoa', 'Xương rồng nở hoa', 'Hoa lớn mùa hè', 41000, 30, 'xuong-rong',
             'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=400'),
            ('opuntia-mini', 'Opuntia mini', 'Tai thỏ nhỏ, gai mềm', 29000, 70, 'xuong-rong',
             'https://images.unsplash.com/photo-1516205651411-aa062d60b2f3?w=400'),
            ('cereus-night', 'Xương rồng đêm', 'Thân dài, chịu khô', 36000, 36, 'xuong-rong',
             'https://images.unsplash.com/photo-1438109491414-7196495b3b0f?w=400'),
            ('mammillaria', 'Mammillaria', 'Tròn lông mịn, hoa vòng', 34000, 40, 'xuong-rong',
             'https://images.unsplash.com/photo-1519336056116-9d7682cbf04f?w=400'),
            ('kim-tien', 'Kim tiền', 'Cây kim tiền phong thủy', 250000, 12, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1509423350716-97f9360b4e09?w=400'),
            ('phat-loc', 'Phát lộc', 'Cây phát lộc may mắn', 120000, 25, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400'),
            ('van-loc', 'Vạn lộc', 'Lá đỏ xanh bóng', 98000, 30, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1512428555758-2fe32d5a7d0a?w=400'),
            ('ngoc-ngan', 'Ngọc ngân', 'Lá sọc bạc, dễ nhân', 88000, 33, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1585320806297-9794b3e7eeae?w=400'),
            ('truc-phat-loc', 'Trúc phát lộc', 'Bụi lá xanh ôm vàng', 195000, 16, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1551892583-d8e919a8c3b4?w=400'),
            ('loc-vung', 'Lộc vừng', 'Tán lá rộng, hoa đỏ nổi bật', 165000, 10, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1614594975525-e45190c55d0b?w=400'),
            ('kim-ngan', 'Kim ngân', 'Thân xi măng lá xanh nhỏ', 142000, 19, 'cay-phong-thuy',
             'https://images.unsplash.com/photo-1509587584298-0f3b3a3a1797?w=400'),
        ]
        for slug, name, desc, price, stock, cat_slug, img_url in products_data:
            cat = Category.objects.get(slug=cat_slug)
            Product.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'price': price,
                    'stock': stock,
                    'category': cat,
                    'status': 'active',
                    'image_url': img_url,
                }
            )

        # Cập nhật image_url cho TẤT CẢ sản phẩm hiện có (kể cả thêm tay)
        slug_to_url = {slug: img for slug, _, _, _, _, _, img in products_data}
        for p in Product.objects.all():
            if p.slug in slug_to_url:
                p.image_url = slug_to_url[p.slug]
                p.save()

        # Đơn hàng mẫu: 30 đơn trong 7 ngày gần nhất (user1), idempotent theo UUID
        legacy_order_keys = [
            'seed-delivered-1',
            'seed-shipped-1',
            'seed-confirmed-1',
            'seed-pending-1',
            'seed-cancelled-1',
            'seed-delivered-2',
        ]
        for lk in legacy_order_keys:
            Order.objects.filter(id=uuid.uuid5(ORDER_SEED_NS, lk)).delete()

        product_slugs = [row[0] for row in products_data]
        districts = [
            'Quận 1',
            'Quận 3',
            'Quận 5',
            'Quận Phú Nhuận',
            'Quận Bình Thạnh',
            'TP. Thủ Đức',
            'Quận Tân Bình',
        ]
        streets = [
            'Lê Lợi',
            'Nguyễn Huệ',
            'Trần Hưng Đạo',
            'Hoàng Diệu',
            'Phạm Văn Đồng',
            'Cách Mạng Tháng 8',
            'Nguyễn Văn Linh',
        ]
        note_pool = [
            '',
            '',
            'Giao giờ hành chính',
            'Gọi trước khi giao',
            'Để trước cửa',
            'Khách đổi ý — đã hủy',
        ]
        status_cycle = [
            'delivered',
            'delivered',
            'shipped',
            'confirmed',
            'pending',
            'cancelled',
        ]
        week_seconds = 7 * 24 * 3600
        now = timezone.now()

        n_orders = 0
        for i in range(30):
            key = f'seed-week-{i}'
            oid = uuid.uuid5(ORDER_SEED_NS, key)
            frac_old = (29 - i) / 29.0 if 29 else 0.0
            jitter = timedelta(minutes=(i * 37) % 720, seconds=(i * 91) % 60)
            created_at = now - timedelta(seconds=int(frac_old * week_seconds)) - jitter

            status = status_cycle[i % len(status_cycle)]
            addr = (
                f'{10 + (i % 90)} {streets[i % len(streets)]}, '
                f'Phường {(i % 15) + 1}, {districts[i % len(districts)]}, TP.HCM'
            )
            phone = f'09{(12345678 + i * 104729) % 100000000:08d}'
            note = note_pool[i % len(note_pool)] if status != 'cancelled' else note_pool[-1]

            n_lines = 1 + (i % 3)
            line_specs = []
            for j in range(n_lines):
                slug = product_slugs[(i + j * 5) % len(product_slugs)]
                qty = 1 + ((i + j * 2) % 4)
                line_specs.append((slug, qty))

            rows = []
            total = 0
            for slug, qty in line_specs:
                prod = Product.objects.get(slug=slug)
                price = prod.price
                sub = price * qty
                total += sub
                rows.append((prod, qty, price, sub))

            order, _ = Order.objects.update_or_create(
                id=oid,
                defaults={
                    'user': user1,
                    'status': status,
                    'shipping_address': addr,
                    'shipping_phone': phone,
                    'total_amount': total,
                    'note': note,
                },
            )
            order.items.all().delete()
            for prod, qty, price, subtotal in rows:
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    product_name=prod.name,
                    price=price,
                    quantity=qty,
                    subtotal=subtotal,
                )
            Order.objects.filter(pk=order.pk).update(created_at=created_at, updated_at=created_at)
            n_orders += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Da seed {n_orders} don hang mau (user1), phan bo trong 7 ngay gan nhat.'
            )
        )

        self.stdout.write(self.style.SUCCESS('Seed data hoan tat!'))
