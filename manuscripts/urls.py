
from django.urls import path

from manuscripts import views

app_name = "manuscripts"

urlpatterns = [
    path('<journal_id>/submit', views.SubmitManuscript.as_view()),
]
