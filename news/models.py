from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """User profile to store profile picture and additional author info."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True, 
                                    help_text='Author profile picture')
    bio         = models.TextField(max_length=500, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name or self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile when a User is created."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Automatically save UserProfile when User is saved."""
    instance.profile.save()


class Language(models.Model):
    """Supported site languages — drives all content isolation."""
    code        = models.CharField(max_length=10, unique=True)  # 'en' | 'rw'
    name        = models.CharField(max_length=100)              # English
    native_name = models.CharField(max_length=100)              # Ikinyarwanda
    flag_emoji  = models.CharField(max_length=10, blank=True)
    is_default  = models.BooleanField(default=False)
    is_active   = models.BooleanField(default=True)
    order       = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Language.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class MainCategory(models.Model):
    """
    Top-level navigation buckets, one set per language.
    EN: Rwanda / Africa / World / Research Paper
    RW: U Rwanda / Afurika / Isi / Inyandiko z'Ubushakashatsi
    """
    language = models.ForeignKey(Language, on_delete=models.CASCADE,
                                 related_name='main_categories')
    name     = models.CharField(max_length=150)
    slug     = models.SlugField(max_length=150)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering  = ['order']
        unique_together = ('language', 'slug')
        verbose_name        = 'Main Category'
        verbose_name_plural = 'Main Categories'

    def __str__(self):
        return f"[{self.language.code.upper()}] {self.name}"

    def get_absolute_url(self):
        return reverse('news:category', kwargs={
            'lang_code': self.language.code,
            'cat_slug':  self.slug,
        })


class SubCategory(models.Model):
    """
    Topic filters, INDEPENDENT of main category.
    The same 10 topics (Politics, Economy, …) apply to every main category.
    One set per language — EN and RW have their own rows.

    EN: Politics / Economy / Education / Society / Culture & Arts /
        Science & Tech / Religion / Environment / Health / Trends
    RW: Politiki / Ubukungu / Uburezi / Sosiyete / Umuco & Ubugeni /
        Ubumenyi & Ikoranabuhanga / Iyobokamana / Ibidukikije / Ubuzima / Ibigezweho
    """
    language = models.ForeignKey(Language, on_delete=models.CASCADE,
                                 related_name='sub_categories')
    name     = models.CharField(max_length=150)
    slug     = models.SlugField(max_length=150)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering  = ['order']
        unique_together = ('language', 'slug')
        verbose_name        = 'Sub Category'
        verbose_name_plural = 'Sub Categories'

    def __str__(self):
        return f"[{self.language.code.upper()}] {self.name}"

    def get_absolute_url(self):
        return reverse('news:subcategory', kwargs={
            'lang_code': self.language.code,
            'sub_slug':  self.slug,
        })


class Article(models.Model):
    STATUS = [('draft', 'Draft'), ('published', 'Published')]

    language      = models.ForeignKey(Language, on_delete=models.CASCADE,
                                      related_name='articles')
    title         = models.CharField(max_length=300)
    slug          = models.SlugField(max_length=300, unique=True)
    main_category = models.ForeignKey(MainCategory, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='articles')
    sub_category  = models.ForeignKey(SubCategory, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='articles')
    author        = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      null=True, blank=True, related_name='articles')

    summary        = models.TextField(max_length=600, blank=True, verbose_name='Lead')
    content        = models.TextField()
    featured_image = models.ImageField(upload_to='articles/%Y/%m/', blank=True, null=True)
    image_caption  = models.CharField(max_length=250, blank=True)

    status      = models.CharField(max_length=10, choices=STATUS, default='draft')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_breaking = models.BooleanField(default=False)

    views        = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f"[{self.language.code.upper()}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug, n = base, 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:article', kwargs={
            'lang_code': self.language.code,
            'slug':      self.slug,
        })

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    @property
    def comment_count(self):
        return self.comments.filter(is_approved=True).count()


class Comment(models.Model):
    article     = models.ForeignKey(Article, on_delete=models.CASCADE,
                                    related_name='comments')
    name        = models.CharField(max_length=100)
    email       = models.EmailField()
    body        = models.TextField(max_length=1000)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.name} on "{self.article.title[:40]}"'


class SiteSettings(models.Model):
    site_name       = models.CharField(max_length=100, default='The Perspectives')
    location        = models.CharField(max_length=100, blank=True, default='Kigali, Rwanda')
    phone          = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    tagline         = models.CharField(max_length=200, blank=True, default='Research · Rwanda · Africa · World')
    mooto_en         = models.CharField(max_length=300, blank=True)
    mooto_rw         = models.CharField(max_length=300, blank=True)
    facebook_url    = models.URLField(blank=True)
    twitter_url     = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    youtube_url    = models.URLField(blank=True)
    instagram_url   = models.URLField(blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name
