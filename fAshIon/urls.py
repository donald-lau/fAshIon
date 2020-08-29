"""backend_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from fAshIon.backend_script.gui import image_search
from fAshIon.backend_script.graph import get_default_graphs
from fAshIon.backend_script.prediction import predict, set_user
from fAshIon.backend_script.autocomplete import get_onto_vocabs
from fAshIon.backend_script.users import update_pref, get_user_pref, get_user_outfit, del_user_pref_outfit, \
    delete_item_in_outfit, update_outfit, new_image_for_outfit, get_user_summary, add_outfit
urlpatterns = [
    path('admin/', admin.site.urls),
    path('predict/', predict),
    path('image_search/', image_search),
    path('get_default_graph/', get_default_graphs),
    path('get_onto_vocabs/', get_onto_vocabs),
    path('set_user/', set_user),
    path('add_outfit/', add_outfit),
    path('update_pref/', update_pref),
    path('get_user_pref/', get_user_pref),
    path('del_user_pref_outfit/', del_user_pref_outfit),
    path('delete_item_in_outfit/', delete_item_in_outfit),
    path('update_outfit/', update_outfit),
    path('new_image_for_outfit/', new_image_for_outfit),
    path('get_user_summary/', get_user_summary),
    path('get_user_outfit/', get_user_outfit)
]


