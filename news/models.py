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


class ResearchField(models.Model):
    """
    Academic discipline / research field (language-scoped).
    EN: Economics, Public Health, Education, Political Science, Environment,
        Agriculture, Technology, Sociology, Law, Medicine …
    """
    language = models.ForeignKey(Language, on_delete=models.CASCADE,
                                 related_name='research_fields')
    name     = models.CharField(max_length=150)
    slug     = models.SlugField(max_length=150)
    order    = models.IntegerField(default=0)

    class Meta:
        ordering        = ['order']
        unique_together = ('language', 'slug')
        verbose_name        = 'Research Field'
        verbose_name_plural = 'Research Fields'

    def __str__(self):
        return f"[{self.language.code.upper()}] {self.name}"

    def get_absolute_url(self):
        return reverse('news:research_field', kwargs={
            'lang_code':   self.language.code,
            'field_slug':  self.slug,
        })


class ResearchPaper(models.Model):
    """
    A peer-reviewed / academic research paper uploaded to the site.

    Key fields
    ──────────
    language        — drives which language edition this paper belongs to
    title           — paper title
    slug            — URL-friendly unique key (auto-generated from title)
    authors         — free-text list of author names (comma-separated)
    institution     — publishing institution / university
    research_field  — academic field (FK to ResearchField)
    sub_category    — news sub-category tag (optional cross-link)
    abstract        — executive summary shown on listing & detail pages
    pdf_file        — the actual paper PDF (uploaded to media/papers/)
    external_url    — alternatively link to an external DOI / journal URL
    cover_image     — optional cover / thumbnail image
    keywords        — comma-separated keywords for searching
    doi             — Digital Object Identifier (e.g. 10.1234/abc)
    journal         — journal or conference name
    volume / issue / pages — bibliographic data
    published_date  — official publication date of the paper
    status          — draft | published
    is_featured     — show in featured section
    is_peer_reviewed — mark as peer-reviewed
    views / downloads — usage counters
    """

    STATUS = [('draft', 'Draft'), ('published', 'Published')]

    PEER_REVIEW_CHOICES = [
        ('yes',     'Peer Reviewed'),
        ('no',      'Not Peer Reviewed'),
        ('pending', 'Under Review'),
    ]

    # ── Identity ─────────────────────────────────────────────────
    language       = models.ForeignKey(Language, on_delete=models.CASCADE,
                                       related_name='research_papers')
    title          = models.CharField(max_length=400,
                                      help_text='Full title of the paper')
    slug           = models.SlugField(max_length=400, unique=True, blank=True)
    sub_title      = models.CharField(max_length=400, blank=True,
                                      help_text='Subtitle (optional)')

    # ── Classification ────────────────────────────────────────────
    research_field = models.ForeignKey(ResearchField, on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       related_name='papers',
                                       help_text='Primary academic discipline')
    sub_category   = models.ForeignKey(SubCategory, on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       related_name='research_papers',
                                       help_text='News topic tag (cross-links with news)')

    # ── Authorship ────────────────────────────────────────────────
    authors        = models.TextField(
                        help_text='Comma-separated list of author names. '
                                  'E.g. "Dr. Jane Uwimana, Prof. John Habimana"')
    institution    = models.CharField(max_length=300, blank=True,
                                      help_text='Publishing institution / university')
    contact_email  = models.EmailField(blank=True,
                                       help_text='Corresponding author email (optional)')

    # ── Bibliographic data ────────────────────────────────────────
    journal        = models.CharField(max_length=300, blank=True,
                                      help_text='Journal or conference name')
    volume         = models.CharField(max_length=50, blank=True,
                                      help_text='Volume number')
    issue          = models.CharField(max_length=50, blank=True,
                                      help_text='Issue number')
    pages          = models.CharField(max_length=50, blank=True,
                                      help_text='Page range, e.g. "12–34"')
    doi            = models.CharField(max_length=200, blank=True,
                                      verbose_name='DOI',
                                      help_text='Digital Object Identifier, e.g. 10.1234/abc')
    issn           = models.CharField(max_length=20, blank=True,
                                      verbose_name='ISSN',
                                      help_text='International Standard Serial Number')
    isbn           = models.CharField(max_length=20, blank=True,
                                      verbose_name='ISBN',
                                      help_text='For books / book chapters')
    published_date = models.DateField(null=True, blank=True,
                                      help_text='Official publication date of the paper')

    # ── Content ───────────────────────────────────────────────────
    abstract       = models.TextField(
                        help_text='Full abstract / executive summary (displayed on site)')
    keywords       = models.CharField(max_length=500, blank=True,
                                      help_text='Comma-separated keywords for search & SEO')
    methodology    = models.TextField(blank=True,
                                      help_text='Brief methodology description (optional)')
    findings       = models.TextField(blank=True,
                                      help_text='Key findings / conclusions (optional)')

    # ── Files & Links ─────────────────────────────────────────────
    pdf_file       = models.FileField(upload_to='papers/pdfs/%Y/',
                                      blank=True, null=True,
                                      help_text='Upload the paper PDF')
    cover_image    = models.ImageField(upload_to='papers/covers/%Y/',
                                       blank=True, null=True,
                                       help_text='Cover image or thumbnail')
    external_url   = models.URLField(blank=True,
                                     help_text='External DOI / journal URL '
                                               '(used if no PDF is uploaded)')
    supplementary  = models.FileField(upload_to='papers/supplementary/%Y/',
                                      blank=True, null=True,
                                      help_text='Supplementary data file (optional)')

    # ── Peer review & status ──────────────────────────────────────
    peer_reviewed  = models.CharField(max_length=10,
                                      choices=PEER_REVIEW_CHOICES,
                                      default='no')
    status         = models.CharField(max_length=10,
                                      choices=STATUS, default='draft')
    is_featured    = models.BooleanField(default=False,
                                         help_text='Feature on Research Paper homepage block')
    is_open_access = models.BooleanField(default=True,
                                          verbose_name='Open Access',
                                          help_text='Mark paper as open access')

    # ── Usage counters ────────────────────────────────────────────
    views          = models.PositiveIntegerField(default=0, editable=False)
    downloads      = models.PositiveIntegerField(default=0, editable=False)

    # ── Timestamps ────────────────────────────────────────────────
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)
    submitted_at   = models.DateTimeField(null=True, blank=True,
                                          help_text='Date submitted to the site')

    class Meta:
        ordering            = ['-published_date', '-created_at']
        verbose_name        = 'Research Paper'
        verbose_name_plural = 'Research Papers'

    def __str__(self):
        return f"[{self.language.code.upper()}] {self.title[:80]}"

    # ── Auto-slug ─────────────────────────────────────────────────
    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:390]
            slug, n = base, 1
            while ResearchPaper.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"; n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:research_paper', kwargs={
            'lang_code': self.language.code,
            'slug':      self.slug,
        })

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def increment_downloads(self):
        self.downloads += 1
        self.save(update_fields=['downloads'])

    # ── Helpers ───────────────────────────────────────────────────
    @property
    def author_list(self):
        """Return list of individual author names."""
        return [a.strip() for a in self.authors.split(',') if a.strip()]

    @property
    def keyword_list(self):
        """Return list of keywords."""
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    @property
    def has_pdf(self):
        return bool(self.pdf_file)

    @property
    def download_url(self):
        """Return PDF URL if uploaded, otherwise external URL."""
        if self.pdf_file:
            return self.pdf_file.url
        return self.external_url or None

    @property
    def citation_count(self):
        return self.citations.count()

    @property
    def comment_count(self):
        return self.paper_comments.filter(is_approved=True).count()

    @property
    def doi_url(self):
        if self.doi:
            return f"https://doi.org/{self.doi}"
        return None


class PaperComment(models.Model):
    """Reader comment on a research paper."""
    paper       = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE,
                                    related_name='paper_comments')
    name        = models.CharField(max_length=100)
    email       = models.EmailField()
    affiliation = models.CharField(max_length=200, blank=True,
                                   help_text='Institution / affiliation (optional)')
    body        = models.TextField(max_length=2000)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        verbose_name        = 'Paper Comment'
        verbose_name_plural = 'Paper Comments'

    def __str__(self):
        return f'{self.name} on "{self.paper.title[:40]}"'


class Citation(models.Model):
    """
    A citation of a ResearchPaper by another paper or external source.
    Allows tracking who cites a given paper.
    """
    paper        = models.ForeignKey(ResearchPaper, on_delete=models.CASCADE,
                                     related_name='citations')
    cited_by     = models.CharField(max_length=400,
                                    help_text='Title of the citing paper')
    cited_by_doi = models.CharField(max_length=200, blank=True,
                                    verbose_name='Citing paper DOI')
    cited_by_url = models.URLField(blank=True,
                                   help_text='URL of the citing paper')
    cited_by_authors = models.CharField(max_length=300, blank=True)
    year         = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-created_at']
        verbose_name        = 'Citation'
        verbose_name_plural = 'Citations'

    def __str__(self):
        return f'"{self.cited_by[:60]}" cites {self.paper.title[:40]}'
