from django.contrib import admin
from django.contrib.auth.models import User

from djangoapps.rootapp.models import SiteUser


admin.site.register(User, SiteUser)
@admin.register(SiteUser)
class AdminUserPerson(admin.ModelAdmin):
    # list_display = ('person', 'learning', 'role')
    # list_filter = ['learning']
    #search_fields = ['learning']
    pass

