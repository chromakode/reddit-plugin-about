GridView = Backbone.View.extend({
    events: {
    },

    itemViews: {},
    initialize: function() {
        this.collection.on('reset', this.addAll, this)
        this.collection.on('all', this.render, this)
    },

    createItemView: function(model) {
        return new Backbone.View({model: model})
    },

    addOne: function(model) {
        if (!this.itemViews[model.cid]) {
            var view = this.createItemView(model)
            this.itemViews[model.cid] = view
        }
    },

    addAll: function() {
        this.collection.each(_.bind(this.addOne, this))
    },

    render: function() {
        var gridWidth = this.$el.width(),
            gridHeight = 0,
            pos = {x:0, y:0},
            sortKey = this.collection.state && this.collection.state.get('sort')

        _.each(this.itemViews, function(view, cid) {
            var model = this.collection.getByCid(cid),
                viewWidth = view.$el.outerWidth(true),
                viewHeight = view.$el.outerHeight(true)

            if (pos.x + viewWidth > gridWidth) {
                pos.x = 0
                pos.y += viewHeight
            }
            gridHeight = pos.y + viewHeight

            view.$el.css({
                'position': 'absolute',
                'left': pos.x,
                'top': pos.y
            })

            if (sortKey) {
                view.$el.toggleClass('novalue', !model.has(sortKey))
            }

            pos.x += viewWidth
        }, this)

        this.$el.css('height', gridHeight)
        return this
    }
})
