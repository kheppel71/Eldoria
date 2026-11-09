"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls starting with `admin/`
(the `admin/` part should not be included again here).

"""

from django.urls import path
from .views import world_map_view, world_map_data_api, world_map_live_api
from evennia.web.admin.urls import urlpatterns as evennia_admin_urlpatterns

# add patterns here
urlpatterns = [
    path("worldmap/", world_map_view, name="world_map"),
    path("worldmap/api/data/", world_map_data_api, name="world_map_data_api"),
    path("worldmap/api/live/", world_map_live_api, name="world_map_live_api"),
]

# read by Django
urlpatterns = urlpatterns + evennia_admin_urlpatterns
