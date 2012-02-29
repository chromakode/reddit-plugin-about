SortRouter = Backbone.Router.extend({
    routes: {
        'sort/:sortId/': 'sort',
    },

    initialize: function(options) {
        this.collection = options.collection
    },

    sort: function(sortId) {
        this.collection.state.set('sort', sortId)
    }
})

DropdownView = Backbone.View.extend({
    events: {
        'click .choice': 'select'
    },

    initialize: function(options) {
        this.attribute = options.attribute
        this.model.on('change:' + this.attribute, this.render, this)
    },

    render: function() {
        var choice = this.model.get(this.attribute),
            $choice = this.$('.drop-choices .choice-' + choice)

        this.$('.drop-choices .selected').removeClass('selected')
        $choice.addClass('selected')
        this.$('.dropdown .selected').text($choice.text())
        return this
    },

    select: function(e) {
        var choice = $(e.target).attr('class').match(/choice-(.*)/)[1]
        this.model.set(this.attribute, choice)
        this.trigger('select', choice)
    }
})

TeamMember = Backbone.Model.extend({
    idAttribute: 'name',
    initialize: function() {
        this.set('random', Math.random())
    }
})

SortableCollection = Backbone.Collection.extend({
    model: TeamMember,

    initialize: function(models, options) {
        this.sorts = options.sorts
        this.state = options.state || new Backbone.Model({
            sort: null
        })
        this.state.on('change:sort', this.sort, this)
    },

    comparator: function(model) {
        var sort = this.sorts.get(this.state.get('sort'))
        if (!sort) {
            return
        }
        return sort.get('dir') * model.get(sort.id) || model.get('random')
    }
})

PersonView = Backbone.View.extend({
})

PeopleGridView = GridView.extend({
    createItemView: function(model) {
        return new PersonView({
            el: this.$('.'+model.id),
            model: model
        })
    }
})

teamSorts = new Backbone.Collection
team = new SortableCollection(null, {sorts: teamSorts})
alumni = new SortableCollection(null, {sorts: teamSorts, state: team.state})

r.about.pages['about-team'] = function() {
    var sortDropdown = new DropdownView({
        el: $('#about-team .sort-menu'),
        model: team.state,
        attribute: 'sort'
    })

    var teamGrid = new PeopleGridView({
        el: $('#team-grid'),
        collection: team
    })

    var alumniGrid = new PeopleGridView({
        el: $('#alumni-grid'),
        collection: alumni
    })

    var sortRouter = new SortRouter({collection: team})
    if (!Backbone.history.start()) {
        // Default to the random sort if no sort is in the URL.
        team.state.set('sort', 'random')
    }
}
