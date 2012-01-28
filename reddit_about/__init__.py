from r2.lib.plugin import Plugin

class About(Plugin):
    def add_routes(self, mc):
        mc('/about/:action', controller='about')

    def load_controllers(self):
        from about import AboutController
