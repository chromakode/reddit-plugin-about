from pylons import request, g
from r2.controllers import add_controller
from pylons.i18n import _
from r2.controllers.reddit_base import RedditController
from r2.models import *
from r2.lib.pages import Templated, BoringPage
from r2.lib.menus import NavMenu, NavButton, OffsiteButton
from r2.lib.template_helpers import comment_label

import re
import random
from itertools import chain
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
    def __init__(self, quote, images, stats, events, sites):
        Templated.__init__(self)
        self.quote = quote
        self.images = images
        self.stats = stats
        self.events = events
        self.sites = sites

class Team(Templated):
    def __init__(self, team, alumni, sorts, extra_sorts):
        Templated.__init__(self)
        self.team = team
        self.alumni = alumni
        self.sorts = sorts + extra_sorts

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

@add_controller
class AboutController(RedditController):
    def GET_index(self):
        quote = self._get_quote()
        images = self._get_images()

        stats = g.memcache.get('about_reddit_stats')

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
            {'date': localdate(2012, 1, 18), 'class': 'culture important', 'title': 'SOPA blackout', 'url': 'http://blog.reddit.com/2012/01/stopped-they-must-be-on-this-all.html'},
            {'date': localdate(2012, 3, 8), 'class': 'org important', 'title': 'CEO announced', 'url': 'http://blog.reddit.com/2012/03/new-reddit-ceo-reporting-for-duty.html'},
            {'date': localdate(2012, 4, 1), 'class': 'culture', 'title': 'reddit timeline', 'url': 'http://blog.reddit.com/2012/03/introducing-reddit-timeline.html'},
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
        sorts = [
             {'id': 'random', 'title': _('random'), 'dir': 1},
             {'id': 'new', 'title': _('new'), 'dir': -1},
             {'id': 'top', 'title': _('top'), 'dir': -1},
             {'id': 'beard', 'title': _('beard'), 'dir': -1},
             {'id': 'pyro', 'title': _('pyromania'), 'dir': -1},
             {'id': 'wpm', 'title': _('words per minute'), 'dir': -1},
        ]

        extra_sorts = [
             {'id': 'starcraft', 'title': _('love of starcraft'), 'dir': -1},
             {'id': 'shatner', 'title': _('love of william shatner'), 'dir': -1},
             {'id': 'arnold', 'title': _('love of arnold schwarzenegger'), 'dir': -1},
             {'id': 'spy', 'title': _('most likely to be a spy'), 'dir': -1},
             {'id': 'pokemon', 'title': _('love of Pokemon'), 'dir': -1},
             {'id': 'scorpions', 'title': _('fear of scorpions'), 'dir': -1},
             {'id': 'zombies', 'title': _('outrunning zombies'), 'dir': -1},
             {'id': 'cycling', 'title': _('longest distance on a bicycle'), 'dir': -1},
             {'id': 'cartman', 'title': _('Eric Cartman impression'), 'dir': -1},
             {'id': 'whales', 'title': _('fear of whales'), 'dir': -1},
             {'id': 'pronunciation', 'title': _('pronunciation'), 'dir': -1},
             {'id': 'giants', 'title': _('giants schwag'), 'dir': -1},
             {'id': 'mornings', 'title': _('early riser'), 'dir': -1},
             {'id': 'pings', 'title': _('number of pings required, Vasily'), 'dir': -1},
             {'id': 'rabbits', 'title': _('number of rabbits owned'), 'dir': -1},
        ]

        team = [
            {"beard": 6, "description": "", "favorite_subreddits": ["", "/r/tldr", "/r/diablo", "/r/AskScience", "/r/tipofmytongue"], "name": "Jason Harvey", "new": 201101, "pyro": 9, "role": "Systems Administrator", "role_details": "linux magician", "starcraft": -9999, "top": 1.83, "username": "alienth"},
            {"beard": 0, "description": "", "favorite_subreddits": [], "name": "Marta Gossage", "pyro": 0, "role": "", "role_details": "", "shatner": 9999, "top": 1.55, "username": "bitcrunch"},
            {"arnold": 9999, "beard": 2, "description": "", "favorite_subreddits": ["/r/AskReddit", "/r/foodforthought", "/r/relationship_advice", "/r/woahdude"], "name": "Brian Simpson", "new": 201106, "pyro": 0, "role": "Programmer", "role_details": "", "top": 1.75, "username": "bsimpson"},
            {"beard": 4, "description": "Max makes your web browser do stuff. Occasionally he draws aliens.", "favorite_subreddits": ["/r/starcraft", "/r/programming", "/r/askscience", "/r/theoryofreddit"], "name": "Max Goodman", "new": 201104, "pyro": 2, "role": "JavaScript Apologist", "role_details": "breaks things", "spy": 9999, "top": 1.68, "username": "chromakode", "wpm": 100},
            {"beard": 0, "description": "Our first graduate from our esteemed internship program!", "favorite_subreddits": ["/r/fifthworldproblems", "/r/aww", "/r/AskScience", "/r/harrypotheads"], "name": "Alex Angel", "new": 201006, "pokemon": 9999, "pyro": 6, "role": "Product Marketing Manager", "role_details": "bringer of baked goods", "top": 1.63, "username": "cupcake1713", "wpm": 88},
            {"beard": 10, "description": "Erik is our general manager and nerd herder. He has an awesome dog named Mog who can often be found around the office.", "favorite_subreddits": ["/r/fifthworldproblems"], "name": "Erik Martin", "new": 200810, "pyro": 6, "role": "General Manager", "role_details": "psychic detective", "scorpions": 9999, "top": 1.83, "username": "hueypriest", "wpm": 12},
            {"beard": 3, "description": "Hacks reddit by day, races motorcycles by night. Or is it the other way around?", "favorite_subreddits": ["/r/motorcycles", "/r/forza", "/r/theoryofreddit", "/r/TheBook"], "name": "Logan Hanks", "new": 201106, "pyro": 3, "role": "Programmer", "role_details": "\\m/", "top": 1.83, "username": "intortus", "wpm": 9999},
            {"beard": 0, "description": "", "favorite_subreddits": [], "name": "Jena Donlin", "new": 201101, "pyro": 1, "role": "Business Operations", "role_details": "", "top": 1.73, "username": "jenakalif", "wpm": 60, "zombies": 9999},
            {"beard": 8, "cycling": 100, "description": "Sneezes chronically. Attempts to make things less annoying. Sometimes fails.", "favorite_subreddits": [], "name": "Keith Mitchell", "new": 201106, "pyro": 4, "role": "Programmer", "role_details": "annoyance reducer", "top": 1.82, "username": "kemitche"},
            {"beard": 0, "cartman": 9999, "description": "When she's not thinking about second breakfast, Adriana makes sure ad campaigns go off smoothly.", "favorite_subreddits": ["/r/funny", "/r/fffffffuuuuuuuuuuuu", "/r/dubstep"], "name": "Adriana Gadala-Maria", "new": 201106, "pyro": 9, "role": "Digital Sales Planner", "role_details": "ad keeper", "top": 1.65, "username": "kirbyrules", "wpm": 72},
            {"beard": 0, "description": "Deals with people so they don't have to.", "favorite_subreddits": ["/r/skyrim", "/r/ladyboners", "/r/TodayILearned"], "name": "Kristine Smith", "new": 201104, "pyro": 8, "role": "Online Advertising Specialist", "role_details": "self serve guru", "top": 1.52, "username": "krispykrackers", "whales": 9999, "wpm": 70},
            {"beard": 0, "description": "", "favorite_subreddits": [], "name": "Lia Navarro", "pyro": 0, "role": "", "role_details": "", "top": 1.7, "username": "pixelinaa"},
            {"beard": 2, "description": "", "favorite_subreddits": ["/r/ultimate", "r/depthhub", "r/fifthworldpics", "r/eatsandwiches", "r/sanfrancisco"], "name": "Josh Wardle", "new": 201109, "pronunciation": 9999, "pyro": 1, "role": "", "role_details": "erstwhile gremlin", "top": 1.82, "username": "powerlanguage"},
            {"beard": 0, "description": "Handles corporate things.", "favorite_subreddits": ["/r/iama", "/r/madmen", "/r/feminisms"], "giants": 9999, "name": "Rebecca Eisenberg", "new": 201202, "pyro": 8, "role": "General Counsel", "role_details": "bounty hunter", "top": 1.63, "username": "rebecalyn", "wpm": 101},
            {"beard": 1, "description": "Our personal puertorrique&#241;o pyromaniac pilot. The best days for him involve home made sangria, wrangling servers, and plenty of small fires.", "favorite_subreddits": ["/r/aviation", "/r/aww", "/r/iama"], "name": "Ricky Ramirez", "new": 201109, "pyro": 10, "role": "Systems Administrator", "role_details": "reboot master", "top": 1.65, "username": "rram", "wpm": 60},
            {"beard": 0, "description": "Valerie drinks a lot of coffee and writes code. She believes almost anything can be improved by adding robots.", "favorite_subreddits": ["/r/depthhub", "/r/foodforthought", "/r/dataisbeautiful"], "mornings": 9999, "name": "Valerie Hajdik", "new": 201204, "pyro": 8, "role": "Programmer", "role_details": "generalist", "top": 1.7, "username": "shlurbee", "wpm": 109},
            {"beard": 9, "description": "Neil tirelessly torches troublemakers in TF2. When he's not doing that he writes code. For a time, he was the only programmer at reddit.", "favorite_subreddits": ["/r/dogs", "/r/truetf2", "/r/boardgames"], "name": "Neil Williams", "new": 201011, "pings": 1, "pyro": 3, "role": "Lead Programmancer", "role_details": "mm mhm mmm!!", "top": 1.72, "username": "spladug", "wpm": 111},
            {"beard": 0, "description": "what is this i don't even", "favorite_subreddits": [], "name": "Yishan Wong", "new": 201202, "pyro": 1, "rabbits": 3, "role": "CEO", "role_details": "sparklepants", "top": 1.74, "username": "yishan", "wpm": 91},
        ]

        alumni = [
             {'username': 'spez', 'new': 0},
             {'username': 'kn0thing', 'new': 0},
             {'username': 'jedberg', 'new': 2},
             {'username': 'KeyserSosa', 'new': 1},
             {'username': 'ketralnis', 'new': 3},
             {'username': 'raldi', 'new': 4},
        ]

        content = Team(team, alumni, sorts, extra_sorts)
        return AboutPage('about-team', _('we spend our days building reddit.'), _('about the reddit team'), content).render()

    def GET_postcards(self):
        postcard_count = '&#32;<span class="count">...</span>&#32;'
        content = Postcards()
        return AboutPage('about-postcards', _('you\'ve sent us over %s postcards.') % postcard_count, _('postcards'), content).render()

    def GET_alien(self):
        colors = (
            ('orangered', '#ff5700'),
            ('eye color', '#ff4500'),
            ('upvote', '#ff8b60'),
            ('neutral', '#c6c6c6'),
            ('downvote', '#9494ff'),
            ('light bg', '#eff7ff'),
            ('header', '#cee3f8'),
            ('ui text', '#336699'),
        )
        content = AlienMedia(colors=colors)
        return AboutPage('about-alien', _('I also do birthday parties.'), _('the alien'), content).render()

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
