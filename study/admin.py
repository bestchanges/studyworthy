from django.contrib import admin

# Register your models here.
from .models import Course, UserProfile, Author


class AuthorInline(admin.StackedInline):
    model = Author


class AdminUser(admin.ModelAdmin):
    exclude = ['skype']
    inlines = [AuthorInline]


class AdminCourse(admin.ModelAdmin):
    list_display = ('title', 'state')
    list_filter = ['state']
    search_fields = ['title', 'slug']


admin.site.register(Author)
admin.site.register(UserProfile, AdminUser)
admin.site.register(Course, AdminCourse)
