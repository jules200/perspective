from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('auth', '0012_alter_user_first_name_max_length')]

    operations = [
        migrations.CreateModel('Language', fields=[
            ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('code',        models.CharField(max_length=10, unique=True)),
            ('name',        models.CharField(max_length=100)),
            ('native_name', models.CharField(max_length=100)),
            ('flag_emoji',  models.CharField(blank=True, max_length=10)),
            ('is_default',  models.BooleanField(default=False)),
            ('is_active',   models.BooleanField(default=True)),
            ('order',       models.IntegerField(default=0)),
        ], options={'ordering':['order'],'verbose_name':'Language'}),

        migrations.CreateModel('SiteSettings', fields=[
            ('id',              models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('site_name',       models.CharField(default='The Perspectives', max_length=100)),
            ('tagline',         models.CharField(blank=True, default='Research · Rwanda · Africa · World', max_length=200)),
            ('facebook_url',    models.URLField(blank=True)),
            ('twitter_url',     models.URLField(blank=True)),
            ('whatsapp_number', models.CharField(blank=True, max_length=20)),
        ], options={'verbose_name':'Site Settings','verbose_name_plural':'Site Settings'}),

        migrations.CreateModel('MainCategory', fields=[
            ('id',       models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('name',     models.CharField(max_length=150)),
            ('slug',     models.SlugField(max_length=150)),
            ('order',    models.IntegerField(default=0)),
            ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='main_categories', to='news.language')),
        ], options={'ordering':['order'],'verbose_name':'Main Category','verbose_name_plural':'Main Categories'}),

        migrations.CreateModel('SubCategory', fields=[
            ('id',       models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('name',     models.CharField(max_length=150)),
            ('slug',     models.SlugField(max_length=150)),
            ('order',    models.IntegerField(default=0)),
            ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                           related_name='sub_categories', to='news.language')),
        ], options={'ordering':['order'],'verbose_name':'Sub Category','verbose_name_plural':'Sub Categories'}),

        migrations.CreateModel('Article', fields=[
            ('id',            models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('title',         models.CharField(max_length=300)),
            ('slug',          models.SlugField(max_length=300, unique=True)),
            ('summary',       models.TextField(blank=True, max_length=600)),
            ('content',       models.TextField()),
            ('featured_image',models.ImageField(blank=True, null=True, upload_to='articles/%Y/%m/')),
            ('image_caption', models.CharField(blank=True, max_length=250)),
            ('status',        models.CharField(choices=[('draft','Draft'),('published','Published')], default='draft', max_length=10)),
            ('is_featured',   models.BooleanField(default=False)),
            ('is_trending',   models.BooleanField(default=False)),
            ('is_breaking',   models.BooleanField(default=False)),
            ('views',         models.PositiveIntegerField(default=0)),
            ('created_at',    models.DateTimeField(auto_now_add=True)),
            ('updated_at',    models.DateTimeField(auto_now=True)),
            ('published_at',  models.DateTimeField(blank=True, null=True)),
            ('language',      models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                related_name='articles', to='news.language')),
            ('author',        models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='articles', to='auth.user')),
            ('main_category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='articles', to='news.maincategory')),
            ('sub_category',  models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                                related_name='articles', to='news.subcategory')),
        ], options={'ordering':['-published_at','-created_at']}),

        migrations.CreateModel('Comment', fields=[
            ('id',          models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('name',        models.CharField(max_length=100)),
            ('email',       models.EmailField()),
            ('body',        models.TextField(max_length=1000)),
            ('created_at',  models.DateTimeField(auto_now_add=True)),
            ('is_approved', models.BooleanField(default=False)),
            ('article',     models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='comments', to='news.article')),
        ], options={'ordering':['created_at']}),

        migrations.AlterUniqueTogether('maincategory', unique_together={('language','slug')}),
        migrations.AlterUniqueTogether('subcategory',  unique_together={('language','slug')}),
    ]
