from django.urls import path

from . import views

app_name = "reviews"


urlpatterns = [
    path("", views.index, name="index"),
    path("no-cards-to-review/", views.no_cards_to_review, name="no_cards_to_review"),
    path("start/", views.start, name="start"),
    path("show-current-card/", views.show_current_card, name="show_current_card"),
    path("move-to-next-card/", views.move_to_next_card, name="move_to_next_card"),
    path("end/", views.end, name="end"),
    path("reveal-answer/", views.reveal_answer, name="reveal_answer"),
    path("answer-card/", views.answer_card, name="answer_card"),
    path("<review_id>/", views.details, name="details"),
]
