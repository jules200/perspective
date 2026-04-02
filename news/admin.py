from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Language, MainCategory, SubCategory, Article, Comment, SiteSettings


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


admin.site.site_header = 'The Perspectives — Admin'
admin.site.site_title  = 'Perspectives Admin'
admin.site.index_title = 'News Management'
