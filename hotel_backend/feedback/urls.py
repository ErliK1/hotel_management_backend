from django.urls import path, include
from .views import FeedbackCreateAPIView, FeedbackListAPIView, FeedbackAverageAndTotal, FeedbackViewedChangeAPIView

urlpatterns = [
    path('create/', FeedbackCreateAPIView.as_view(),),
    path('list/', FeedbackListAPIView.as_view()),
    path('average/', FeedbackAverageAndTotal.as_view()),
    path('check/', FeedbackViewedChangeAPIView.as_view())
]