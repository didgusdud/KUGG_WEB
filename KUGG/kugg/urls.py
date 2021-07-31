from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    path('info_list', views.info_list, name='info_list'),
    path('detail_info_list', views.detail_info_list, name='detail_info_list'),
    path('detail_info_search', views.detail_info_search, name='detail_info_search'),
    path('object_list', views.object_list, name='object_list'),
    path('platinum_object_list', views.platinum_object_list, name='platinum_object_list'),
    path('champion_list', views.champion_list, name='champion_list'),
    path('selected_champion_list', views.info_list, name='selected_champion_list'),
    path('champion_analysis', views.champion_analysis, name='champion_analysis'),
    #path('object_list/<int:전령>', views.object_list_updated, name='object_list_updated'),   
]