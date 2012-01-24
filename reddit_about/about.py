from pylons import request, g
from r2.controllers import add_controller
from r2.controllers.reddit_base import RedditController
from r2.lib.pages import *

class About(Templated):
    pass

@add_controller
class AboutController(RedditController):
    def GET_index(self):
        return About().render()
