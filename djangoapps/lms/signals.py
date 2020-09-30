import django.dispatch

lesson_available = django.dispatch.Signal(providing_args=["flow_lesson", "by_user"])
lesson_unavailable = django.dispatch.Signal(providing_args=["flow_lesson", "by_user"])
flow_started = django.dispatch.Signal(providing_args=["flow"])
