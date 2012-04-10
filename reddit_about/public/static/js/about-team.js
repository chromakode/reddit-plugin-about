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
    idAttribute: 'username',

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

PersonDetailsPopup = Backbone.View.extend({
    id: 'person-overlay',
    events: {
        'click .close': 'hide'
    },

    template: _.template(
         '<button class="close">x</button><div class="top"><strong class="name"><%= data.name %></strong> <em class="role"><%= data.role %></em></div>'
        +'<p class="description"><%= data.description %></p>'
        +'<div class="etc"><a href="http://www.reddit.com/user/<%= data.username %>" target="_blank">reddit.com/user/<%= data.username %></a></div>',
        null, {variable: 'data'}
    ),

    initialize: function() {
        $('body').click(_.bind(function(ev) {
            if (!this.targetView) {
                return
            }

            var parents = $(ev.target).parents()
            if (!parents.is(this.$el) && !parents.is(this.targetView.$el)) {
                this.hide()
            }
        }, this))
        $(window).resize(_.bind(this.position, this))
    },

    render: function() {
        this.$el.empty().append(this.template(this.model.toJSON()))
    },

    position: function() {
        var avatar = this.targetView.$('.avatar'),
            personPos = avatar.offset(),
            leftSide = personPos.left < this.$el.parent().width() / 2

        this.$el
            .css({
                top: personPos.top,
                left: personPos.left + (leftSide ? avatar.outerWidth(true) : -this.$el.width())
            })
            .removeClass('left right')
            .addClass(leftSide ? 'left' : 'right')
    },

    show: function(model, view) {
        this.hide()
        this.model = model
        this.targetView = view

        this.render()
        this.position()
        this.$el.show()

        this.targetView.$el.addClass('focused')
        this.trigger('show')
    },

    hide: function() {
        if (this.targetView) {
            this.targetView.$el.removeClass('focused')
        }
        this.$el.hide()
        this.trigger('hide')
        this.model = null
        this.targetView = null
    },

    toggle: function(model, view) {
        if (this.model == model) {
            this.hide()
        } else {
            this.show(model, view)
        }
    }
})

PersonView = Backbone.View.extend({
    events: {
        'click': 'showInfo'
    },

    showInfo: function() {
        this.options.popup.toggle(this.model, this)
    }
})

PeopleGridView = GridView.extend({
    initialize: function() {
        GridView.prototype.initialize.apply(this)
        this.collection.on('reset', this.options.popup.hide, this.options.popup)
        this.options.popup.on('show', this.focus, this)
        this.options.popup.on('hide', this.unfocus, this)
    },

    createItemView: function(model) {
        return new PersonView({
            el: this.$('.'+model.id),
            model: model,
            popup: this.options.popup
        })
    },

    focus: function() {
        this.$el.addClass('focusing')
    },

    unfocus: function() {
        this.$el.removeClass('focusing')
    },
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

    new scrollFixed($('#about-team .sort-menu'))

    var personPopup = new PersonDetailsPopup()
    $('#about-team').append(personPopup.el)

    var teamGrid = new PeopleGridView({
        el: $('#team-grid'),
        collection: team,
        popup: personPopup
    })

    var alumniGrid = new PeopleGridView({
        el: $('#alumni-grid'),
        collection: alumni,
        popup: personPopup
    })

    var sortRouter = new SortRouter({collection: team})
    if (!Backbone.history.start()) {
        // Default to the random sort if no sort is in the URL.
        team.state.set('sort', 'random')
    }
}
