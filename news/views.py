from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Language, MainCategory, SubCategory, Article, Comment
from .forms import CommentForm

VALID_LANGS = ('en', 'rw')


# ── helpers ─────────────────────────────────────────────────────────────────

def _lang(lang_code):
    """Return Language object or 404."""
    return get_object_or_404(Language, code=lang_code, is_active=True)


def _base(lang_code):
    """Base published queryset for a language."""
    lang = _lang(lang_code)
    return lang, Article.objects.filter(status='published', language=lang)\
                                .select_related('main_category', 'sub_category', 'author')


# ── language switch & root redirect ─────────────────────────────────────────

def root_redirect(request):
    """/ → /en/"""
    return redirect('/en/')


def switch_lang(request):
    """POST /switch-lang/  body: lang=en|rw  next=<path>"""
    if request.method == 'POST':
        code = request.POST.get('lang', 'en')
        if code not in VALID_LANGS:
            code = 'en'
        # next_url is the current page path; swap the lang prefix
        next_url = request.POST.get('next', f'/{code}/')
        # Replace leading language prefix in the path
        parts = next_url.strip('/').split('/', 1)
        if parts and parts[0] in VALID_LANGS:
            rest = parts[1] if len(parts) > 1 else ''
            next_url = f'/{code}'
            # next_url = f'/{code}/{rest}'
        else:
            next_url = f'/{code}/'
        return redirect(next_url)
    return redirect('/en/')


# ── pages ────────────────────────────────────────────────────────────────────

def home(request, lang_code):
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang, qs = _base(lang_code)
    cats     = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs     = list(SubCategory.objects.filter(language=lang).order_by('order'))

    # Build as list of (cat, articles) so template can iterate easily
    cat_blocks = [(c, list(qs.filter(main_category=c)[:4])) for c in cats]

    return render(request, 'news/home.html', {
        'lang_code':    lang_code,
        'lang':         lang,
        'cats':         cats,
        'subs':         subs,
        'cat_blocks':   cat_blocks,
        'featured':     list(qs.filter(is_featured=True)[:5]),
        'breaking':     list(qs.filter(is_breaking=True)[:6]),
        'trending':     list(qs.filter(is_trending=True)[:8]),
        'latest':       list(qs[:12]),
    })


def category(request, lang_code, cat_slug):
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang, qs = _base(lang_code)
    cat  = get_object_or_404(MainCategory, language=lang, slug=cat_slug)
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))
    arts = list(qs.filter(main_category=cat))
    return render(request, 'news/listing.html', {
        'lang_code':  lang_code, 'lang': lang,
        'cats':       list(MainCategory.objects.filter(language=lang).order_by('order')),
        'subs':       subs,
        'articles':   arts,
        'active_cat': cat,
        'active_sub': None,
        'page_title': cat.name,
    })


def subcategory(request, lang_code, sub_slug):
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang, qs = _base(lang_code)
    sub  = get_object_or_404(SubCategory, language=lang, slug=sub_slug)
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))
    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    arts = list(qs.filter(sub_category=sub))
    return render(request, 'news/listing.html', {
        'lang_code':  lang_code, 'lang': lang,
        'cats':       cats, 'subs': subs,
        'articles':   arts,
        'active_cat': None,
        'active_sub': sub,
        'page_title': sub.name,
    })


def cat_sub(request, lang_code, cat_slug, sub_slug):
    """Filter by both main category AND sub-category."""
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang, qs = _base(lang_code)
    cat  = get_object_or_404(MainCategory, language=lang, slug=cat_slug)
    sub  = get_object_or_404(SubCategory, language=lang, slug=sub_slug)
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))
    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    arts = list(qs.filter(main_category=cat, sub_category=sub))
    return render(request, 'news/listing.html', {
        'lang_code':  lang_code, 'lang': lang,
        'cats':       cats, 'subs': subs,
        'articles':   arts,
        'active_cat': cat,
        'active_sub': sub,
        'page_title': f"{cat.name} — {sub.name}",
    })


def article_detail(request, lang_code, slug):
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang = _lang(lang_code)
    art  = get_object_or_404(Article, slug=slug, status='published', language=lang)
    art.increment_views()

    related  = list(Article.objects.filter(
        status='published', language=lang, main_category=art.main_category
    ).exclude(pk=art.pk)[:4])
    trending = list(Article.objects.filter(
        status='published', language=lang, is_trending=True
    ).exclude(pk=art.pk)[:6])

    comments = art.comments.filter(is_approved=True)
    form     = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.article = art
            c.save()
            ok = ('Igitekerezo cyawe cyoherejwe, kirindirwa kwemezwa.'
                  if lang_code == 'rw'
                  else 'Comment submitted — awaiting approval.')
            messages.success(request, ok)
            return redirect(art.get_absolute_url())

    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))

    return render(request, 'news/article_detail.html', {
        'lang_code': lang_code, 'lang': lang,
        'article':  art, 'related': related, 'trending': trending,
        'comments': comments, 'form': form,
        'cats': cats, 'subs': subs,
    })


def search(request, lang_code):
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang, qs = _base(lang_code)
    q    = request.GET.get('q', '').strip()
    arts = []
    if q:
        arts = list(qs.filter(
            Q(title__icontains=q) | Q(summary__icontains=q) | Q(content__icontains=q)
        ))
    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))
    return render(request, 'news/search.html', {
        'lang_code': lang_code, 'lang': lang,
        'query': q, 'articles': arts, 'count': len(arts),
        'cats': cats, 'subs': subs,
    })
