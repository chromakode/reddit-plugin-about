import sys
import calendar
import time
import datetime
import httplib2
import ConfigParser
import sqlalchemy as sa
from pylons import g
from r2.models import Account, Link, Comment, Vote
from r2.lib.db.tdb_sql import get_rel_table
from r2.lib.utils import timeago, fetch_things2

def subreddit_stats(config):
    def sr_ids(query):
        return set(thing.sr_id for thing in fetch_things2(query))

    link_srs = sr_ids(Link._query(Link.c._date > timeago('1 week'), data=True))
    comment_srs = sr_ids(Comment._query(Comment.c._date > timeago('1 week'), data=True))
    return {'subreddits_active_past_week': len(link_srs | comment_srs)}

def vote_stats(config):
    stats = {}

    link_votes = Vote.rel(Account, Link)
    comment_votes = Vote.rel(Account, Comment)

    for name, rel in (('link', link_votes), ('comment', comment_votes)):
        table = get_rel_table(rel._type_id)[0]
        q = table.count(table.c.date > timeago('1 day'))
        stats[name+'_vote_count_past_day'] = q.execute().fetchone()[0]

    stats['vote_count_past_day'] = stats['link_vote_count_past_day'] + stats['comment_vote_count_past_day']
    return stats

def ga_stats(config):
    stats = {}

    from apiclient.discovery import build
    from oauth2client.file import Storage
    from oauth2client.client import OAuth2WebServerFlow
    from oauth2client.tools import run, FLAGS

    storage = Storage('analytics_credentials.dat')
    credentials = storage.get()

    if credentials is None or credentials.invalid == True:
        flow = OAuth2WebServerFlow(
            client_id=config.get('about_stats', 'ga_client_id'),
            client_secret=config.get('about_stats', 'ga_client_secret'),
            scope='https://www.googleapis.com/auth/analytics.readonly',
            user_agent='reddit-stats/1.0')

        FLAGS.auth_local_webserver = False
        credentials = run(flow, storage)

    http = httplib2.Http()
    http = credentials.authorize(http)

    analytics = build("analytics", "v3", http=http)

    today = datetime.date.today()
    first_day, last_day = calendar.monthrange(today.year, today.month)
    start_date = (today - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    visitors = analytics.data().ga().get(
        ids='ga:24573069',
        start_date=start_date,
        end_date=end_date,
        metrics='ga:visitors',
        dimensions='ga:country',
        filters='ga:customVarValue3=@loggedin'
    ).execute()

    stats['country_count_past_month'] = visitors['totalResults']
    stats['redditors_visited_past_month'] = int(visitors['totalsForAllResults']['ga:visitors'])
    return stats

def update_stats(config):
    stats = {}
    def run_stats(f):
        start_time = time.time()
        stats.update(f(config))
        end_time = time.time()
        print >> sys.stderr, '%s took %0.2f seconds.' % (f.__name__, end_time - start_time)

    print >> sys.stderr, 'recalculating reddit stats...'
    run_stats(subreddit_stats)
    run_stats(vote_stats)
    run_stats(ga_stats)
    g.memcache.set('about_reddit_stats', stats)

def main(config_file):
    parser = ConfigParser.RawConfigParser()
    with open(config_file, "r") as cf:
        parser.readfp(cf)
    update_stats(parser)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "USAGE: %s /path/to/config-file.ini" % sys.argv[0]
        sys.exit(1)

    main(sys.argv[1])
