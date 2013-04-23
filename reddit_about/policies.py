import re

from pylons import g
from pylons.i18n import _
from BeautifulSoup import BeautifulSoup, Tag

from r2.lib.base import abort
from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.models.subreddit import Frontpage
from r2.models.wiki import WikiPage, WikiRevision
from r2.lib.db import tdb_cassandra
from r2.lib.filters import unsafe, wikimarkdown, generate_table_of_contents
from r2.lib.jsontemplates import ThingJsonTemplate
from r2.lib.validator import validate, nop
from pages import PolicyPage, PolicyView


class PolicyViewJsonTemplate(ThingJsonTemplate):
    _data_attrs_ = dict(
        body_html="body_html",
        toc_html="toc_html",
        revs="revs",
        display_rev="display_rev",
    )

    def kind(self, wrapped):
        return "Policy"


@add_controller
class PoliciesController(RedditController):
    @validate(requested_rev=nop('v'))
    def GET_policy_page(self, page, requested_rev):
        if page == 'privacypolicy':
            wiki_name = g.wiki_page_privacypolicy
            pagename = _('privacy policy')
        elif page == 'useragreement':
            wiki_name = g.wiki_page_useragreement
            pagename = _('user agreement')
        else:
            abort(404)

        wp = WikiPage.get(Frontpage, wiki_name)

        revs = [rev for rev in wp.get_revisions()
                if rev._get('reason') and not rev.is_hidden]
        rev_info = [{
            'id': str(rev._id),
            'title': rev._get('reason'),
        } for rev in revs]

        if requested_rev:
            try:
                display_rev = WikiRevision.get(requested_rev, wp._id)
            except (tdb_cassandra.NotFound, ValueError):
                abort(404)
        else:
            display_rev = revs[0]

        doc_html = wikimarkdown(display_rev.content, include_toc=False)
        soup = BeautifulSoup(doc_html.decode('utf-8'))
        toc = generate_table_of_contents(soup, prefix='section')
        self._number_sections(soup)
        self._linkify_headings(soup)

        content = PolicyView(
            body_html=unsafe(soup),
            toc_html=unsafe(toc),
            revs=rev_info,
            display_rev=str(display_rev._id),
        )
        return PolicyPage(
            pagename=pagename,
            content=content,
        ).render()

    def _number_sections(self, soup):
        count = 1
        for para in soup.findAll(['p']):
            a = parent = Tag(soup, 'a', [
                ('class', 'section'),
                ('id', 'p_%d' % count),
                ('href', '#p_%d' % count),
            ])
            a.append(str(count))
            para.insert(0, a)
            para.insert(1, ' ')
            count += 1

    def _linkify_headings(self, soup):
        for heading in soup.findAll(['h1', 'h2', 'h3']):
            heading_a = Tag(soup, "a", [('href', '#%s' % heading['id'])])
            heading_a.string = heading.string
            heading.string = ''
            heading.append(heading_a)
