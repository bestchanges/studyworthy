from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

@apphook_pool.register
class MyApphook(CMSApp):
    app_name = "lms_cms"  # must match the application namespace
    name = "LMS App Hook"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["djangoapps.lms_cms.urls"]
