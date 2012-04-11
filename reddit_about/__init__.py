from r2.lib.plugin import Plugin
from r2.lib.app_globals import ConfigValue
from r2.lib.js import Module

def not_in_sr(environ, results):
    return 'subreddit' not in environ and 'sub_domain' not in environ

class About(Plugin):
    config = {
        ConfigValue.int: [
            'about_images_count',
            'about_images_min_score'
        ]
    }

    js = {
        'less': Module('lib/less-1.3.0.min.js', should_compile=False),

        'about': Module('about.js',
            'lib/underscore-1.3.3.js',
            'lib/backbone-0.9.1.js',
            'utils.js',
            'slideshow.js',
            'timeline.js',
            'grid.js',
            'about.js',
            'about-main.js',
            'about-team.js'
        )
    }

    def add_routes(self, mc):
        mc('/about/:action', controller='about', conditions={'function':not_in_sr})

    def load_controllers(self):
        from about import AboutController
