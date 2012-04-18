from pylons import request, g
from r2.controllers import add_controller
from pylons.i18n import _
from r2.controllers.reddit_base import RedditController
from r2.models import *
from r2.lib.pages import Templated, BoringPage
from r2.lib.menus import NavMenu, NavButton
from r2.lib.template_helpers import comment_label

import re
import random
from datetime import datetime

def localdate(*args):
    return datetime(*args, tzinfo=g.tz)

class AboutPage(BoringPage):
    css_class = 'about-page'

    def __init__(self, content_id=None, title_msg=None, pagename=None, content=None, **kw):
        BoringPage.__init__(self, pagename or _('about reddit'), show_sidebar=False, content=content, **kw)
        self.content_id = content_id
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
    def __init__(self, quote, images, stats, events, sites):
        Templated.__init__(self)
        self.quote = quote
        self.images = images
        self.stats = stats
        self.events = events
        self.sites = sites

class Team(Templated):
    def __init__(self, team, alumni, sorts):
        Templated.__init__(self)
        self.team = team
        self.alumni = alumni
        self.sorts = sorts
        sort_buttons = [NavButton(sort['title'], '#sort/'+sort['id'], css_class='choice-'+sort['id']) for sort in sorts]
        self.sort_menu = NavMenu(sort_buttons, title=_('sorted by'), base_path=request.path, type='lightdrop', default='#sort/random')

class Postcards(Templated):
    pass

@add_controller
class AboutController(RedditController):
    def GET_index(self):
        quote = self._get_quote()
        images = self._get_images()

        stats = {
            'active_communities': 3043,
            'active_accounts': 700564,
            'country_count': 300,
            'country_map': '',
        }

        events = [
            {'date': localdate(2005, 6, 23), 'class': 'org important', 'title': 'reddit goes live', 'url': 'http://www.flickr.com/photos/33809408@N00/315068778/'},
            {'date': localdate(2007, 4, 1), 'class': 'culture aprilfools', 'title': 'reddit censors the front page', 'url': 'http://blog.reddit.com/2007/04/reddit-now-doubleplusgood.html'},
            {'date': localdate(2007, 11, 26), 'class': 'culture important', 'title': 'Mr. Splashy Pants', 'url': 'http://www.reddit.com/comments/61gqb/greenpeace_are_having_a_vote_to_name_a_whale_they'},
            {'date': localdate(2008, 3, 12), 'class': 'org important', 'title': 'subreddits launched', 'url': 'http://blog.reddit.com/2008/03/make-your-own-reddit.html'},
            {'date': localdate(2008, 4, 1), 'class': 'culture aprilfools', 'title': 'karma exchange marketplace opens', 'url': 'http://blog.reddit.com/2008/04/put-those-dollars-into-something-safe.html'},
            {'date': localdate(2008, 6, 17), 'class': 'org important', 'title': 'reddit goes open source', 'url': 'http://blog.reddit.com/2008/06/reddit-goes-open-source.html'},
            {'date': localdate(2008, 9, 9), 'class': 'culture important', 'title': 'crowbar shipped to CERN', 'url': 'http://blog.reddit.com/2008/09/crowbar-headcrab-and-half-life-strategy.html'},
            {'date': localdate(2009, 11, 10), 'class': 'org important', 'title': 'move to the cloud', 'url': 'http://blog.reddit.com/2009/11/moving-to-cloud.html'},
            {'date': localdate(2009, 4, 1), 'class': 'culture aprilfools', 'title': 'long overdue styling update', 'url': 'http://blog.reddit.com/2009/04/long-overdue-update.html'},
            {'date': localdate(2009, 8, 24), 'class': 'culture', 'title': 'reddit\'s fantastic voyage', 'url': 'http://blog.reddit.com/2009/08/reddits-fatastic-voyage-reddit.html'},
            {'date': localdate(2009, 9, 9), 'class': 'org important', 'title': 'self serve advertising opens', 'url': 'http://blog.reddit.com/2009/12/self-serve-advertising-on-reddit-is-now.html'},
            {'date': localdate(2010, 4, 1), 'class': 'culture aprilfools important', 'title': 'everyone is an admin', 'url': 'http://www.reddit.com/r/reddit.com/comments/bkzbt/everyone_is_fucked_we_are_all_admin/'},
            {'date': localdate(2010, 7, 26), 'class': 'org important', 'title': 'reddit gold released', 'url': 'http://blog.reddit.com/2010/07/reddit-needs-help.html'},
            {'date': localdate(2011, 4, 1), 'class': 'culture aprilfools important', 'title': 'reddit mold', 'url': 'http://blog.reddit.com/2011/04/mold-mph-mmmph-mph.html'},
            {'date': localdate(2011, 10, 18), 'class': 'org important', 'title': '/r/reddit.com archived', 'url': 'http://blog.reddit.com/2011/10/saying-goodbye-to-old-friend-and.html'},
        ]

        sites = [
            {'name': 'redditgifts', 'url': 'http://redditgifts.com', 'icon': 'http://redditgifts.com/favicon.ico'},
            {'name': 'reddit.tv', 'url': 'http://reddit.tv', 'icon': 'http://reddit.tv/favicon.ico'},
            {'name': 'radio reddit', 'url': 'http://radioreddit.com', 'icon': 'http://radioreddit.com/sites/default/files/radioreddit_two_favicon.ico'},
            {'name': 'redditlist', 'url': 'http://redditlist.com', 'icon': 'http://redditlist.com/favicon.ico'},
        ]

        content = About(quote, images, stats, events, sites)
        return AboutPage('about-main', _('we power awesome communities.'), _('about reddit'), content).render()

    def GET_team(self):
        sorts = (
             {'id': 'random', 'title': _('random'), 'dir': 1},
             {'id': 'new', 'title': _('new'), 'dir': 1},
             {'id': 'hot', 'title': _('hot'), 'dir': -1},
             {'id': 'top', 'title': _('top'), 'dir': -1},
             {'id': 'beard', 'title': _('beard'), 'dir': -1},
             {'id': 'pyro', 'title': _('pyromania'), 'dir': -1},
             {'id': 'arnold', 'title': _('love of arnold schwarzenegger'), 'dir': -1},
             {'id': 'spy', 'title': _('most likely to be a spy'), 'dir': -1}
        )

        team = [
             {'username': 'alienth', 'new': 12, 'top': 1.83, 'beard': 8, 'pyro': 10},
             {'username': 'bitcrunch', 'top': 1.55},
             {'username': 'bsimpson', 'top': 1.75, 'arnold': 9999},
             {'username': 'chromakode', 'new': 13, 'top': 1.68, 'beard': 5, 'spy': 9999},
             {'username': 'cupcake1713', 'top': 1.63},
             {'username': 'hueypriest', 'name':'Erik Martin', 'role':'General Manager', 'description':'Erik is our general manager and nerd herder. He has an awesome dog named Mog who can often be found around the office.', 'new': 10, 'top': 1.83, 'beard': 10},
             {'username': 'intortus', 'top': 1.83, 'beard': 5},
             {'username': 'jenakalif', 'top': 1.73},
             {'username': 'kemitche', 'top': 1.82, 'beard': 6},
             {'username': 'kirbyrules', 'top': 1.65},
             {'username': 'krispykrackers', 'top': 1.52},
             {'username': 'pixelinaa', 'top': 1.70},
             {'username': 'powerlanguage', 'top': 1.82},
             {'username': 'rram', 'top': 1.65, 'beard': 3, 'pyro': 10},
             {'username': 'spladug', 'top': 1.72, 'new': 11, 'beard': 10, 'pyro': 5},
             {'username': 'yishan'},
        ]

        alumni = [
             {'username': 'spez', 'new': 0},
             {'username': 'kn0thing', 'new': 0},
             {'username': 'jedberg', 'new': 2},
             {'username': 'KeyserSosa', 'new': 1},
             {'username': 'ketralnis', 'new': 3},
             {'username': 'raldi', 'new': 4},
        ]

        content = Team(team, alumni, sorts)
        return AboutPage('about-team', _('we spend our days building reddit.'), _('about the reddit team'), content).render()

    def GET_postcards(self):
        postcard_count = 6000
        content = Postcards()
        return AboutPage('about-postcards', _('you\'ve sent us over %s postcards.') % postcard_count, _('postcards'), content).render()

    def GET_media(self):
        return AboutPage('about-media', _('I also do birthday parties.'), _('media')).render()

    def GET_guide(self):
        return AboutPage('about-guide', _('new to reddit? welcome.'), _('guide')).render()

    def _parse_title_date(self, date_str):
        if not date_str:
            return None

        parsed_date = None
        try:
            parsed_date = datetime.strptime(date_str, '%m/%d/%y')
        except ValueError:
            pass
        else:
            # Fudge timezone to g.tz
            parsed_date = parsed_date.replace(tzinfo=g.tz)

        return parsed_date

    quote_title_re = re.compile(r'''
        ^
        "(?P<body>[^"]+)"\s*                # "quote"
        --\s*(?P<author>[^,[]+)             # --author
        (?:,\s*(?P<date>\d+/\d+/\d+))?      # , mm/dd/yy *optional*
        \s*(?:\[via\s*(?P<via>[^\]]+)\])?   # [via username] *optional*
        $
    ''', re.VERBOSE)

    def _get_quote(self):
        sr = Subreddit._by_name(g.about_sr_quotes)
        ids = list(sr.get_links('hot', 'all'))
        random.shuffle(ids)
        builder = IDBuilder(ids, skip=True,
                            keep_fn=lambda x: self.quote_title_re.match(x.title),
                            num=1)
        quote_link = builder.get_items()[0][0]

        quote = self.quote_title_re.match(quote_link.title).groupdict()
        quote['date'] = self._parse_title_date(quote['date']) or quote_link._date
        quote['url'] = quote_link.url
        quote['author_url'] = getattr(quote_link, 'author_url', quote['url'])
        quote['via'] = quote['via'] or quote_link.author.name
        quote['via_url'] = '/user/' + quote['via']
        quote['comment_label'], quote['comment_class'] = comment_label(quote_link.num_comments)
        quote['permalink'] = quote_link.permalink
        return quote

    image_title_re = re.compile(r'''
        ^
        (?P<title>[^[]+?)\s*                # photo title
        \s*(?:\[by\s*(?P<author>[^\]]+)\])  # [by author]
        \s*(?:\[via\s*(?P<via>[^\]]+)\])?   # [via username] *optional*
        $
    ''', re.VERBOSE)

    def _get_images(self):
        sr = Subreddit._by_name(g.about_sr_images)
        ids = list(sr.get_links('hot', 'all'))
        builder = IDBuilder(ids, skip=True,
                            keep_fn = lambda x: self.image_title_re.match(x.title)
                                                and x.score >= g.about_images_min_score,
                            num=g.about_images_count)
        image_links = builder.get_items()[0]
        images = []
        for image_link in image_links:
            image = self.image_title_re.match(image_link.title).groupdict()
            image['src'] = image_link.slideshow_src
            image['url'] = image_link.url
            image['author_url'] = getattr(image_link, 'author_url', image['url'])
            image['via'] = image['via'] or image_link.author.name
            image['via_url'] = '/user/' + image['via']
            image['comment_label'], image['comment_class'] = comment_label(image_link.num_comments)
            image['permalink'] = image_link.permalink
            images.append(image)
        return images
