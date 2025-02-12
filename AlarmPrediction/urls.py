"""AlarmPrediction URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url, include	# added an import!
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin

urlpatterns = [
    	# use your app_name here
    url(r'^', include('apps.alarm_prediction_app.urls')),

    url(r'^admin/', admin.site.urls)
]

# urlpatterns += i18n_patterns(
#     url(r'^', include('apps.alarm_prediction_app.urls')),
#     prefix_default_language=False, # < here
# ) 