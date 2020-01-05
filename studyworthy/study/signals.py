from django.db.models.signals import ModelSignal

learning_started_signal = ModelSignal(providing_args=["learning"], use_caching=True)
learning_finished_signal = ModelSignal(providing_args=["learning"], use_caching=True)
lesson_opened_signal = ModelSignal(providing_args=["lesson"], use_caching=True)
