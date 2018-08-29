"""MyMapMatching URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from mapmatching import views as mapmatching_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^mapmatching/getGraphhopperSplitTrajectory/$', mapmatching_views.getGraphhopperSplitTrajectory),
    url(r'^mapmatching/getShowRoute/$', mapmatching_views.getShowRoute),
    url(r'^mapmatching/getMatchGraphhopperID2MyID/$', mapmatching_views.getMatchGraphhopperID2MyID),
    url(r'^mapmatching/getConvertGrophhopperDataToDataBase/$', mapmatching_views.getConvertGrophhopperDataToDataBase),
    url(r'^mapmatching/getConvertGPS/$', mapmatching_views.getConvertGPS),
    url(r'^mapmatching/getCollectRoute/$', mapmatching_views.getCollectRoute),
    url(r'^mapmatching/getSaveGPX/$', mapmatching_views.getSaveGPX, name='saveGPX'),
    url(r'^mapmatching/getSaveName/$', mapmatching_views.getSaveName, name='sendName'),
    url(r'^mapmatching/getCreateRouteTransfer/$', mapmatching_views.getCreateRouteTransfer),
    url(r'^mapmatching/getCreateNodesTable/$', mapmatching_views.getCreateNodesTable),
    url(r'^mapmatching/getCollectPOI/$', mapmatching_views.getCollectPOI),
    url(r'^mapmatching/getSavePOI/$', mapmatching_views.getSavePOI),
    url(r'^mapmatching/getCreateTestSource2DestinationPair/$', mapmatching_views.getCreateTestSource2DestinationPair),
    url(r'^mapmatching/getDoRouteUpdate/$', mapmatching_views.getDoRouteUpdate),
    url(r'^mapmatching/getShowUpdatedRoute/$', mapmatching_views.getShowUpdatedRoute),
    url(r'^mapmatching/getCollectSemanticLabel/$', mapmatching_views.getCollectSemanticLabel),
    url(r'^mapmatching/getSaveSemanticLabel/$', mapmatching_views.getSaveSemanticLabel),
    url(r'^mapmatching/getUserNewLocation/$', mapmatching_views.getUserNewLocation),
]
