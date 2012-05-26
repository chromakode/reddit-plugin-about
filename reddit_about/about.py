import re
import random
import json
from os import path
from itertools import chain
from datetime import datetime

from pylons import request, g
from pylons.i18n import _

from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.models import *
from r2.lib.db.queries import CachedResults
from r2.lib.pages import Templated, BoringPage
from r2.lib.menus import NavMenu, NavButton, OffsiteButton
from r2.lib.template_helpers import comment_label


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
            NavButton(_('alien'), '/alien'),
            #NavButton(_('guide'), '/guide')
        ]
        about_menu = NavMenu(about_buttons, type='tabmenu', base_path='/about/', css_class='about-menu')
        return self.content_stack([AboutTitle(self.title_msg), about_menu, self._content])


class AboutTitle(Templated):
    def __init__(self, message):
        Templated.__init__(self)
        self.message = message


class About(Templated):
    pass


class Team(Templated):
    def __init__(self, team, alumni, sorts, extra_sorts):
        Templated.__init__(self, team=team, alumni=alumni, sorts=sorts + extra_sorts)

        sort_buttons = []
        extra_sort_index = random.randint(len(sorts), len(self.sorts)-1)
        for idx, sort in enumerate(self.sorts):
            css_class = 'choice-'+sort['id']
            if sort in extra_sorts and idx != extra_sort_index:
                css_class += ' hidden-sort'
            button = OffsiteButton(sort['title'], '#sort/'+sort['id'], css_class=css_class)
            sort_buttons.append(button)
        self.sort_menu = NavMenu(sort_buttons, title=_('sorted by'), base_path=request.path, type='lightdrop', default='#sort/random')

        # The caching check won't catch the hidden-sort classes
        self.sort_menu.cachable = False


class Postcards(Templated):
    pass


class AlienMedia(Templated):
    pass


def parse_date_text(date_str):
    if not date_str:
        return None

    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        parsed_date = None
    else:
        # Fudge timezone to g.tz
        parsed_date = parsed_date.replace(tzinfo=g.tz)

    return parsed_date

@add_controller
class AboutController(RedditController):
    @classmethod
    def load_data(cls):
        def load(name):
            with open(path.join(path.dirname(__file__), 'data', name)) as f:
                data = json.load(f)
            return data
        cls.timeline_data = load('timeline.json')
        for idx, event in enumerate(cls.timeline_data):
            cls.timeline_data[idx]['date'] = parse_date_text(event['date'])
        cls.sites_data = load('sites.json')
        cls.team_data = load('team.json')
        cls.colors_data = load('colors.json')

    def GET_index(self):
        quote = self._get_quote()
        images = self._get_images()
        stats = g.memcache.get('about_reddit_stats', None)
        content = About(quote=quote, images=images, stats=stats, events=self.timeline_data, sites=self.sites_data)
        return AboutPage('about-main', _('we power awesome communities.'), _('about reddit'), content).render()

    def GET_team(self):
        content = Team(**self.team_data)
        return AboutPage('about-team', _('we spend our days building reddit.'), _('about the reddit team'), content).render()

    def GET_postcards(self):
        postcard_count = '&#32;<span class="count">...</span>&#32;'
        content = Postcards()
        return AboutPage('about-postcards', _('you\'ve sent us over %s postcards.') % postcard_count, _('postcards'), content).render()

    def GET_alien(self):
        content = AlienMedia(colors=self.colors_data)
        return AboutPage('about-alien', _('I also do birthday parties.'), _('the alien'), content).render()

    def GET_guide(self):
        return AboutPage('about-guide', _('new to reddit? welcome.'), _('guide')).render()

    def _get_hot_posts(self, sr, count, shuffle=False, filter=None):
        links = sr.get_links('hot', 'all')
        assert type(links) is CachedResults
        ids = list(links)
        if shuffle:
            random.shuffle(ids)
        builder = IDBuilder(ids, skip=True,
                            keep_fn=filter if filter is not None
                                    else lambda x: x,
                            num=count)
        return builder.get_items()[0]

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
        quote_link = self._get_hot_posts(sr, count=1, shuffle=True,
            filter=lambda x: self.quote_title_re.match(x.title))[0]

        quote = self.quote_title_re.match(quote_link.title).groupdict()
        quote['date'] = parse_date_text(quote['date']) or quote_link._date
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
        image_links = self._get_hot_posts(sr, count=g.about_images_count,
            filter=lambda x: self.image_title_re.match(x.title)
                             and x.score >= g.about_images_min_score)

        images = []
        for image_link in image_links:
            image = self.image_title_re.match(image_link.title).groupdict()
            image['url'] = image_link.url
            image['src'] = getattr(image_link, 'slideshow_src', image_link.url)
            image['author_url'] = getattr(image_link, 'author_url', image['url'])
            image['via'] = image['via'] or image_link.author.name
            image['via_url'] = '/user/' + image['via']
            image['comment_label'], image['comment_class'] = comment_label(image_link.num_comments)
            image['permalink'] = image_link.permalink
            images.append(image)
        return images
