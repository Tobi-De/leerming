from django.urls import path

from . import views

app_name = "flashcards"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path(
        "create-from-document/", views.create_from_document, name="create_from_document"
    ),
    path("triage/", views.triage, name="triage"),
    path(
        "edit-llm-flashcard/<str:id>/",
        views.edit_llm_flashcard,
        name="edit_llm_flashcard",
    ),
    path("save-llm-flashcards/", views.save_llm_flashcards, name="save_llm_flashcards"),
    path("<int:pk>/edit/", views.edit, name="edit"),
    path("<int:pk>/delete/", views.delete, name="delete"),
    path("<int:pk>/show-answer/", views.show_answer, name="show_answer"),
    path("<int:pk>/show-question/", views.show_question, name="show_question"),
]
