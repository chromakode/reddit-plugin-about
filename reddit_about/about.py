from pylons import request, g
from r2.controllers import add_controller
from pylons.i18n import _
from r2.controllers.reddit_base import RedditController
from r2.lib.pages import *
from r2.lib.menus import NavMenu, NavButton

class AboutPage(BoringPage):
    css_class = "about-page"

    def __init__(self, title_msg=None, pagename=None, **kw):
        BoringPage.__init__(self, pagename or _("about reddit"), show_sidebar=False, **kw)
        self.title_msg = title_msg

    def content(self):
        about_buttons = [
            NavButton(_('about reddit'), '/'),
            NavButton(_('team'), '/team'),
            NavButton(_('postcards'), '/postcards'),
            NavButton(_('media'), '/media'),
            NavButton(_('guide'), '/guide')
        ]
        about_menu = NavMenu(about_buttons, type="tabmenu", base_path="/about/", css_class="about-menu")
        return self.content_stack([AboutTitle(self.title_msg), about_menu, self._content])

class AboutTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message

class About(Templated):
    pass

@add_controller
class AboutController(RedditController):
    def GET_index(self):
        return AboutPage(_('we power awesome communities.'), content=About()).render()

    def GET_team(self):
        return AboutPage(_('we spend our days building reddit.'), content=About()).render()

    def GET_postcards(self):
        postcard_count = 6000
        return AboutPage(_('you\'ve sent us over %s postcards.' % postcard_count), content=About()).render()

    def GET_media(self):
        return AboutPage(_('I also do birthday parties.'), content=About()).render()

    def GET_guide(self):
        return AboutPage(_('new to reddit? welcome.'), content=About()).render()
