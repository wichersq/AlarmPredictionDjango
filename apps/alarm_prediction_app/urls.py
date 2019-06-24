from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^$', views.display_cover, name='cover_page'),
    url(r'^register&login$', views.index),
    url(r'^register$', views.register_account),
    url(r'^login$', views.process_login),
    url(r'^logout$', views.logout),
    
    url(r'^user$', views.display_login, name="main_page"),
    url(r'^create$', views.process_event),
    url(r'^calc_alarm/(?P<event_id>\d+)$', views.calc_alarm),
    url(r'^show/(?P<event_id>\d+)$', views.show_event),
    url(r'^delete/(?P<event_id>\d+)$', views.delete_event),
    url(r'^edit/(?P<event_id>\d+)$', views.display_edit_page),
    url(r'^update/(?P<event_id>\d+)$', views.update_event),
    # url(r'^clear$', views.clear_input),
    url(r'^authorize$', views.get_authorize_calendar),
    url(r'^oauth2_call_back', views.oauth2_call_back),

    url(r'^gcalendar/events$', views.get_g_events),
    url(r'^gcalendar/(?P<index>)\d+/(?P<g_event_id>\w+)$', views.process_calc_g_events),

    #    url(r'^user/(?P<user_id>\d+)/thread/(?P<post_id>\d+)/post_comment$', views.post_comment),
    #    url(r'^user/(?P<user_id>\d+)/thread/(?P<post_id>\d+)/delete$', views.delete_post)
]
