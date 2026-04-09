from django.urls import path
from . import views

# All patterns are mounted under /<lang_code>/  by the root urls.py
# so every URL already carries the language prefix.

app_name = 'news'

urlpatterns = [
    path('',views.home,name='home'),
    path('category/<slug:cat_slug>/', views.category, name='category'),
    path('subcategory/<slug:sub_slug>/',views.subcategory,name='subcategory'),
    # category + sub filter together
    path('category/<slug:cat_slug>/sub/<slug:sub_slug>/', views.cat_sub, name='cat_sub'),
    path('article/<slug:slug>/',views.article_detail, name='article'),
    path('search/',views.search,name='search'),

    # Research papers
    path('research/',                                     views.research_list,  name='research_list'),
    path('research/field/<slug:field_slug>/',             views.research_field, name='research_field'),
    path('research/<slug:slug>/',                         views.research_paper, name='research_paper'),
    path('research/<slug:slug>/download/',                views.research_download, name='research_download'),
]
