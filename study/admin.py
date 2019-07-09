from django.contrib import admin

# Register your models here.
from .models import Course, Profile, Author


class AuthorInline(admin.StackedInline):
    model = Author


class AdminUser(admin.ModelAdmin):
    exclude = ['skype']
    inlines = [AuthorInline]


admin.site.register(Course)
admin.site.register(Author)
admin.site.register(Profile, AdminUser)