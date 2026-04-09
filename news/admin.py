from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django_summernote.admin import SummernoteModelAdmin
from .models import Language, MainCategory, SubCategory, Article, Comment, SiteSettings, UserProfile, ResearchField, ResearchPaper, PaperComment, Citation


class UserProfileInline(admin.StackedInline):
    """Inline profile editor for User admin."""
    model = UserProfile
    fields = ('profile_pic', 'bio')
    extra = 0


class UserAdmin(BaseUserAdmin):
    """Extended User admin with profile picture."""
    inlines = (UserProfileInline,)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display  = ('code','name','native_name','flag_emoji','is_default','is_active','order')
    list_editable = ('is_default','is_active','order')


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display        = ('name','language','slug','order')
    list_filter         = ('language',)
    prepopulated_fields = {'slug':('name',)}
    ordering            = ['language','order']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display        = ('name','language','slug','order')
    list_filter         = ('language',)
    prepopulated_fields = {'slug':('name',)}
    ordering            = ['language','order']
    # NOTE: SubCategory has NO main_category FK — it is language-scoped only.
    # The same sub-categories appear across ALL main categories.


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display      = ('title','language','main_category','sub_category',
                         'author','status','is_featured','is_trending','is_breaking',
                         'views','published_at')
    list_filter       = ('language','status','main_category','sub_category',
                         'is_featured','is_trending','is_breaking')
    search_fields     = ('title','summary','content')
    prepopulated_fields = {'slug':('title',)}
    readonly_fields   = ('views','created_at','updated_at')
    list_editable     = ('status','is_featured','is_trending','is_breaking')
    date_hierarchy    = 'published_at'
    fieldsets = (
        ('Language & Classification', {'fields': ('language','main_category','sub_category','author')}),
        ('Content',   {'fields': ('title','slug','summary','content')}),
        ('Media',     {'fields': ('featured_image','image_caption')}),
        ('Publish',   {'fields': ('status','is_featured','is_trending','is_breaking','published_at')}),
        ('Stats',     {'fields': ('views','created_at','updated_at'),'classes':('collapse',)}),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display  = ('name','email','article','created_at','is_approved')
    list_filter   = ('is_approved',)
    list_editable = ('is_approved',)
    actions       = ['approve']

    def approve(self, request, qs):
        qs.update(is_approved=True)
    approve.short_description = 'Approve selected comments'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name','tagline')


# ═══════════════════════════════════════════════════════
#  RESEARCH PAPER ADMIN
# ═══════════════════════════════════════════════════════

@admin.register(ResearchField)
class ResearchFieldAdmin(admin.ModelAdmin):
    list_display        = ('name', 'language', 'slug', 'order')
    list_filter         = ('language',)
    prepopulated_fields = {'slug': ('name',)}
    ordering            = ['language', 'order']


class CitationInline(admin.TabularInline):
    model  = Citation
    extra  = 1
    fields = ('cited_by', 'cited_by_authors', 'year', 'cited_by_doi', 'cited_by_url')


class PaperCommentInline(admin.TabularInline):
    model  = PaperComment
    extra  = 0
    fields = ('name', 'email', 'affiliation', 'body', 'is_approved')
    readonly_fields = ('name', 'email', 'affiliation', 'body')


@admin.register(ResearchPaper)
class ResearchPaperAdmin(SummernoteModelAdmin):
    summernote_fields = ('abstract', 'methodology', 'findings')

    list_display  = (
        'title', 'language', 'research_field', 'peer_reviewed',
        'status', 'is_featured', 'is_open_access',
        'published_date', 'views', 'downloads',
    )
    list_filter   = (
        'language', 'status', 'research_field', 'peer_reviewed',
        'is_featured', 'is_open_access', 'sub_category',
    )
    search_fields = ('title', 'authors', 'abstract', 'keywords', 'doi', 'institution')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields     = ('views', 'downloads', 'created_at', 'updated_at')
    list_editable       = ('status', 'is_featured', 'peer_reviewed')
    date_hierarchy      = 'published_date'
    inlines             = [CitationInline, PaperCommentInline]

    fieldsets = (
        ('Language & Classification', {
            'fields': ('language', 'research_field', 'sub_category'),
        }),
        ('Title & Authors', {
            'fields': ('title', 'sub_title', 'slug', 'authors',
                       'institution', 'contact_email'),
        }),
        ('Bibliographic Data', {
            'fields': ('journal', 'volume', 'issue', 'pages',
                       'doi', 'issn', 'isbn', 'published_date'),
            'classes': ('collapse',),
        }),
        ('Content', {
            'fields': ('abstract', 'keywords', 'methodology', 'findings'),
        }),
        ('Files & Links', {
            'fields': ('pdf_file', 'cover_image', 'external_url', 'supplementary'),
        }),
        ('Publication Settings', {
            'fields': ('status', 'peer_reviewed', 'is_featured',
                       'is_open_access', 'submitted_at'),
        }),
        ('Stats (read-only)', {
            'fields': ('views', 'downloads', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(PaperComment)
class PaperCommentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'affiliation', 'paper', 'created_at', 'is_approved')
    list_filter   = ('is_approved', 'created_at')
    list_editable = ('is_approved',)
    search_fields = ('name', 'email', 'body', 'paper__title')
    actions       = ['approve_comments']

    def approve_comments(self, request, qs):
        qs.update(is_approved=True)
    approve_comments.short_description = 'Approve selected comments'


@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    list_display  = ('cited_by', 'cited_by_authors', 'year', 'paper')
    list_filter   = ('year',)
    search_fields = ('cited_by', 'cited_by_authors', 'cited_by_doi', 'paper__title')
    raw_id_fields = ('paper',)

admin.site.site_header = 'The Perspectives — Admin'
admin.site.site_title  = 'Perspectives Admin'
admin.site.index_title = 'News Management'
