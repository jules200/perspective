from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Language, MainCategory, SubCategory, Article, Comment, ResearchField, ResearchPaper, PaperComment
from .forms import CommentForm, PaperCommentForm

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
        'latest':       list(qs[:6]),
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

# ═══════════════════════════════════════════════════════
#  RESEARCH PAPER VIEWS
# ═══════════════════════════════════════════════════════

def research_list(request, lang_code):
    """All published research papers for this language."""
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang = _lang(lang_code)

    q      = request.GET.get('q', '').strip()
    field  = request.GET.get('field', '')
    review = request.GET.get('review', '')

    qs = ResearchPaper.objects.filter(
        status='published', language=lang
    ).select_related('research_field', 'sub_category').order_by('-published_date', '-created_at')

    # Filters
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(authors__icontains=q) |
            Q(abstract__icontains=q) | Q(keywords__icontains=q) |
            Q(institution__icontains=q) | Q(doi__icontains=q)
        )
    if field:
        qs = qs.filter(research_field__slug=field)
    if review:
        qs = qs.filter(peer_reviewed=review)

    fields   = list(ResearchField.objects.filter(language=lang).order_by('order'))
    featured = list(ResearchPaper.objects.filter(
        status='published', language=lang, is_featured=True
    ).select_related('research_field')[:3])

    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))

    return render(request, 'news/research_list.html', {
        'lang_code':    lang_code,
        'lang':         lang,
        'papers':       list(qs),
        'featured':     featured,
        'fields':       fields,
        'cats':         cats,
        'subs':         subs,
        'q':            q,
        'active_field': field,
        'active_review': review,
        'total':        qs.count(),
    })


def research_field(request, lang_code, field_slug):
    """Papers filtered by a specific research field."""
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang   = _lang(lang_code)
    rf     = get_object_or_404(ResearchField, language=lang, slug=field_slug)
    papers = list(ResearchPaper.objects.filter(
        status='published', language=lang, research_field=rf
    ).select_related('research_field', 'sub_category').order_by('-published_date'))

    fields = list(ResearchField.objects.filter(language=lang).order_by('order'))
    cats   = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs   = list(SubCategory.objects.filter(language=lang).order_by('order'))

    return render(request, 'news/research_list.html', {
        'lang_code':    lang_code,
        'lang':         lang,
        'papers':       papers,
        'featured':     [],
        'fields':       fields,
        'cats':         cats,
        'subs':         subs,
        'active_field': field_slug,
        'active_rf':    rf,
        'total':        len(papers),
        'q':            '',
        'active_review': '',
    })


def research_paper(request, lang_code, slug):
    """Full research paper detail page."""
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang  = _lang(lang_code)
    paper = get_object_or_404(ResearchPaper, slug=slug, status='published', language=lang)
    paper.increment_views()

    # Related papers — same research field
    related = list(ResearchPaper.objects.filter(
        status='published', language=lang, research_field=paper.research_field
    ).exclude(pk=paper.pk)[:4])

    # Recent papers for sidebar
    recent = list(ResearchPaper.objects.filter(
        status='published', language=lang
    ).exclude(pk=paper.pk).order_by('-published_date')[:6])

    comments     = paper.paper_comments.filter(is_approved=True)
    comment_form = PaperCommentForm()
    citations    = paper.citations.all()

    cats = list(MainCategory.objects.filter(language=lang).order_by('order'))
    subs = list(SubCategory.objects.filter(language=lang).order_by('order'))
    fields = list(ResearchField.objects.filter(language=lang).order_by('order'))

    if request.method == 'POST':
        comment_form = PaperCommentForm(request.POST)
        if comment_form.is_valid():
            c = comment_form.save(commit=False)
            c.paper = paper
            c.save()
            ok = ('Igitekerezo cyawe cyoherejwe, kirindirwa kwemezwa.'
                  if lang_code == 'rw'
                  else 'Comment submitted and awaiting approval.')
            messages.success(request, ok)
            return redirect(paper.get_absolute_url())

    return render(request, 'news/research_paper.html', {
        'lang_code':    lang_code,
        'lang':         lang,
        'paper':        paper,
        'related':      related,
        'recent':       recent,
        'comments':     comments,
        'comment_form': comment_form,
        'citations':    citations,
        'cats':         cats,
        'subs':         subs,
        'fields':       fields,
    })


def research_download(request, lang_code, slug):
    """Serve the PDF and increment download counter."""
    if lang_code not in VALID_LANGS:
        return redirect('/en/')
    lang  = _lang(lang_code)
    paper = get_object_or_404(ResearchPaper, slug=slug, status='published', language=lang)

    if paper.pdf_file:
        paper.increment_downloads()
        return FileResponse(
            paper.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"{paper.slug}.pdf",
        )
    elif paper.external_url:
        paper.increment_downloads()
        return redirect(paper.external_url)

    raise Http404("No PDF available for this paper.")