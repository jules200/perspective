from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from news import views as nv

urlpatterns = [
    # Language switch — POST /switch-lang/
    path('switch-lang/', nv.switch_lang, name='switch_lang'),
    path('summernote/', include('django_summernote.urls')),
    path('admin/', admin.site.urls),

    # Default redirect: / → /en/
    path('', nv.root_redirect, name='root'),

    # Language-prefixed URLs
    path('<str:lang_code>/', include('news.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
