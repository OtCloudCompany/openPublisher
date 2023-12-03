from django.urls import path, include

from accounts import views as profile_views

app_name = "profiles"

urlpatterns = [
    # path('/', include('rest_registration.api.urls')),
    path('create', profile_views.CreateProfile.as_view()),
    path('list', profile_views.ListProfiles.as_view()),
    path('<pk>/delete', profile_views.DeleteProfile.as_view()),
    path('<pk>/update', profile_views.UpdateProfile.as_view()),
    path('<pk>/details', profile_views.ProfileDetails.as_view()),
    path('<pk>/create-address', profile_views.CreateAddress.as_view()),
    path('login', profile_views.Login.as_view()),
]
