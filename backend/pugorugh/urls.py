from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from pugorugh import views

# API endpoints
urlpatterns = format_suffix_patterns([
    url(r'^api/user/login/$', obtain_auth_token, name='login-user'),
    url(r'^api/user/$', views.UserRegisterView.as_view(),
        name='register-user'),
    url(r'^api/dog/$', views.CreateDog.as_view(), name='new-dog'),
    url(r'^api/dog/(?P<pk>\d+)/$',
        views.DestroyDog.as_view(),
        name="dog-delete",
        ),
    url(r'^api/dog/(?P<pk>-?\d+)/(?P<dog_filter>liked|disliked|undecided)/next/$',
        views.RetrieveFilteredDog.as_view(),
        name="filtered-dog-detail",
        ),
    url(r'^api/dog/(?P<pk>\d+)/(?P<dog_status>liked|disliked|undecided)/$',
        views.UpdateDogStatus.as_view(),
        name="update-dog",
        ),
    url(r'^api/user/preferences/$',
        views.RetrieveUpdateUserPreferences.as_view(),
        name="update-user-preferences",
        ),
    url(r'^api/user/isstaff/$',
        views.IsStaff.as_view(),
        name="user-is-staff",
        ),
    url(r'^favicon\.ico$',
        RedirectView.as_view(
            url='/static/icons/favicon.ico',
            permanent=True
        )),
    url(r'^$', TemplateView.as_view(template_name='index.html'))
])
