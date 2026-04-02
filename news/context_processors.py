from .models import Language, MainCategory, SubCategory, SiteSettings


def site_context(request):
    # Detect lang_code from URL (first path segment)
    path_parts = request.path.strip('/').split('/')
    lang_code  = path_parts[0] if path_parts and path_parts[0] in ('en', 'rw') else 'en'

    try:
        lang = Language.objects.get(code=lang_code, is_active=True)
    except Language.DoesNotExist:
        lang = Language.objects.filter(is_active=True).first()
        lang_code = lang.code if lang else 'en'

    cats = list(MainCategory.objects.filter(language=lang).order_by('order')) if lang else []
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))  if lang else []
    all_languages = list(Language.objects.filter(is_active=True).order_by('order'))

    try:
        site_settings = SiteSettings.objects.first()
    except Exception:
        site_settings = None

    return {
        'lang_code':    lang_code,
        'lang':         lang,
        'nav_cats':     cats,
        'nav_subs':     subs,
        'all_languages': all_languages,
        'site_settings': site_settings,
        'current_path':  request.path,
    }
