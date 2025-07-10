from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import index, getData ,  stocks , loginView , logoutView , register ,  buy , sell, landing


urlpatterns = [
    path('', landing, name='landing'),
    path('portfolio/', index, name='index'),
    path('stocks/', stocks, name='stocks'),
    path('market/', stocks, name='market'),
    path('data/', getData, name='data'  ),
    path('login/' , loginView , name  = 'login') ,
    path('logout/' ,  logoutView , name = 'logout') ,
    path('register/'  , register ,  name = 'register'),
    path('buy/<int:id>' , buy,  name ='buy') ,
    path('sell/<int:id>' , sell,  name ='sell')
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
