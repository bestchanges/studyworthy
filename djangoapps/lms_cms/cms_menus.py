from cms.menu_bases import CMSAttachMenu
from django.urls import reverse
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _


class LMSMenu(CMSAttachMenu):
    name = _("lesson menu")

    def get_nodes(self, request):
            return [
                NavigationNode(_("Log in"), reverse('login'), 3, attr={'visible_for_authenticated': False}),
                NavigationNode(_("Log out"), reverse('logout'), 2, attr={'visible_for_anonymous': False}),
            ]

menu_pool.register_menu(LMSMenu)