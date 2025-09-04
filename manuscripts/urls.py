
from django.urls import path

from manuscripts import views

app_name = "manuscripts"

urlpatterns = [
    path('<journal_id>/submit', views.SubmitManuscript.as_view(), name="submit"),
    path('<journal_id>', views.GetLocalManuscripts.as_view(), name="list"),
    path('assigned-reviews', views.AssignedReviews.as_view(), name="assigned-reviews"),
    path('<journal_id>/<manuscript_id>', views.GetLocalManuscriptById.as_view(), name="get"),
    path('<journal_id>/<manuscript_id>/change-status', views.ChangeManuscriptStatus.as_view(), name="change-status"),
    path('<journal_id>/<manuscript_id>/assign-reviewer', views.AssignReviewer.as_view(), name="assign-reviewer"),
    path('<journal_id>/<manuscript_id>/submit-review', views.SubmitReview.as_view(), name="submit-review"),
    path('<journal_id>/<manuscript_id>/submit-corrections', views.SubmitCorrections.as_view(), name="submit-corrections"),
]
