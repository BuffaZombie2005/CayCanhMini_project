from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_add_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image_url',
            field=models.TextField(blank=True, verbose_name='URL ảnh (từ mạng)'),
        ),
    ]
