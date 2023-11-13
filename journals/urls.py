
from django.urls import path

from journals import views

app_name = "journals"

urlpatterns = [
    path('create', views.CreateJournal.as_view()),
    path('<pk>/update', views.UpdateJournal.as_view()),
    path('<pk>/delete', views.DeleteJournal.as_view()),
    path('<pk>/details', views.JournalDetails.as_view()),
    path('list', views.ListJournals.as_view()),
]
