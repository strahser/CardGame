
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.start_battle, name='start_battle'),
    path ('card/', include("Cards.urls")),
    # path('game/', include('game.urls')),
]
