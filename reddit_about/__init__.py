from r2.lib.plugin import Plugin
from r2.lib.js import Module

def not_in_sr(environ, results):
    return 'subreddit' not in environ and 'sub_domain' not in environ

class About(Plugin):
    js = {
        'less': Module('lib/less-1.2.1.min.js', should_compile=False)
    }

    def add_routes(self, mc):
        mc('/about/:action', controller='about', conditions={'function':not_in_sr})

    def load_controllers(self):
        from about import AboutController
