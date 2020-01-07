import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.http import urlencode

from crm.models.crm_models import CourseProduct
from rootapp.models import SiteUser


def index(request):
    courses = CourseProduct.objects.filter(state=CourseProduct.State.ACTIVE)
    context = {
        'courses': courses,
    }
    return render(request, 'index.html', context)


@login_required
def dashboard(request):
    user : SiteUser = request.user
    auth0user = user.social_auth.get(provider='auth0')
    person = user.person
    if 'picture' in auth0user.extra_data and person:
        if auth0user.extra_data['picture'] != person.avatar_url:
            person.avatar_url = auth0user.extra_data['picture']
            person.save()
    if person and not person.first_name:
        # First try to get name, next is to get email
        name = user.first_name or auth0user.extra_data.get('name') or auth0user.extra_data.get('email')
        if name:
            # use name before @ in email as first_name
            name = name.split('@', 1)[0]
            person.first_name = name
            person.save()

    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email'],
    }

    return render(request, 'dashboard.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })


def logout_view(request):
    logout(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN, settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)
