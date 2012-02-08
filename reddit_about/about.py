from pylons import request, g
from r2.controllers import add_controller
from pylons.i18n import _
from r2.controllers.reddit_base import RedditController
from r2.models import *
from r2.lib.pages import Templated, BoringPage
from r2.lib.menus import NavMenu, NavButton
from r2.lib.template_helpers import comment_label

import random

class AboutPage(BoringPage):
    css_class = 'about-page'

    def __init__(self, title_msg=None, pagename=None, content=None, **kw):
        BoringPage.__init__(self, pagename or _('about reddit'), show_sidebar=False, content=content, **kw)
        self.title_msg = title_msg

    def content(self):
        about_buttons = [
            NavButton(_('about reddit'), '/'),
            NavButton(_('team'), '/team'),
            NavButton(_('postcards'), '/postcards'),
            NavButton(_('media'), '/media'),
            NavButton(_('guide'), '/guide')
        ]
        about_menu = NavMenu(about_buttons, type='tabmenu', base_path='/about/', css_class='about-menu')
        return self.content_stack([AboutTitle(self.title_msg), about_menu, self._content])

class AboutTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message

class About(Templated):
    def __init__(self, quote, images, stats, sites):
        Templated.__init__(self)
        self.quote = quote
        self.images = images
        self.stats = stats
        self.sites = sites

@add_controller
class AboutController(RedditController):
    def GET_index(self):
        quote = self._get_quote()

        images = [
            {'src': '',
             'title': 'test slideshow image',
             'url': '',
             'author': 'tester',
             'author_url': '',
             'sr': 'about_images',
             'via': 'tester'}
        ]

        stats = {
            'active_communities': 3043,
            'active_accounts': 700564,
            'country_count': 300,
            'country_map': '',
        }

        sites = [
            {'name': 'redditgifts', 'url': 'http://redditgifts.com', 'icon': 'http://redditgifts.com/favicon.ico'},
            {'name': 'reddit.tv', 'url': 'http://reddit.tv', 'icon': 'http://reddit.tv/favicon.ico'},
            {'name': 'radio reddit', 'url': 'http://radioreddit.com', 'icon': 'http://radioreddit.com/sites/default/files/radioreddit_two_favicon.ico'},
            {'name': 'redditlist', 'url': 'http://redditlist.com', 'icon': 'http://redditlist.com/favicon.ico'},
        ]

        content = About(quote, images, stats, sites)
        return AboutPage(_('we power awesome communities.'), _('about reddit'), content).render()

    def GET_team(self):
        return AboutPage(_('we spend our days building reddit.'), _('about the reddit team')).render()

    def GET_postcards(self):
        postcard_count = 6000
        return AboutPage(_('you\'ve sent us over %s postcards.' % postcard_count), _('postcards')).render()

    def GET_media(self):
        return AboutPage(_('I also do birthday parties.'), _('media')).render()

    def GET_guide(self):
        return AboutPage(_('new to reddit? welcome.'), _('guide')).render()

    def _get_quote(self):
        sr = Subreddit._by_name(g.about_sr_quotes)
        ids = list(sr.get_links('hot', 'all'))
        quote_link = Link._by_fullname(random.choice(ids))

        quote = {}
        quote['body'], quote['author'] = quote_link.title.rsplit('--', 1)
        quote['body'] = quote['body'].strip(' "')
        quote['author_url'] = getattr(quote_link, 'author_url', None)
        quote['url'] = quote_link.url
        quote['date'] = quote_link._date
        quote['via'] = Account._byID(quote_link.author_id).name
        quote['comment_label'], quote['comment_class'] = comment_label(quote_link.num_comments)
        quote['permalink'] = quote_link.make_permalink_slow()
        return quote
