var baseURL = 'http://postcards.redditstatic.com/',
    mapURL = _.template('http://maps.google.com/?q=<%= d.lat %>,<%= d.long %>'),
    mapImageURL = _.template('http://maps.googleapis.com/maps/api/staticmap?zoom=<%= d.zoom %>&size=<%= d.width %>x<%= d.height %>&sensor=false&markers=size:mid%7Ccolor:red%7C<%= d.lat %>,<%= d.long %>')

Postcard = Backbone.Model.extend({})
PostcardsPlaceholder = Backbone.Model.extend({})

PostcardCollection = Backbone.Collection.extend({
    model: Postcard,
    url: baseURL + 'postcards-latest.js',
    chunkSize: null,
    loadedChunks: {},

    load: function(callback) {
        this.fetch({success: _.bind(function(collection, response) {
            this.chunkSize = response.postcards.length
            this.totalCount = response.total_postcard_count
            this.chunkIndex = response.index
            this.chunkCount = _.size(this.chunkIndex)
            _.each(this.chunkIndex, function(bounds, idx) {
                this.add(new PostcardsPlaceholder({chunkStart: bounds[0], id: 'chunk'+idx}))
            }, this)
            callback()
        }, this)})
    },

    ensureLoaded: function(cardId, callback) {
        var chunkId
        for (var i = 0; i < this.chunkCount; i++) {
            var bounds = this.chunkIndex[i]
            if (cardId >= bounds[0] && cardId <= bounds[1]) {
                chunkId = i
                break
            }
        }
        if (chunkId == null) {
            // :(
            return
        }

        if (chunkId in this.loadedChunks) {
            if (callback) {
                callback()
            }
        } else {
            this.fetch({chunk: chunkId, success: callback})
        }
    },

    fetch: function(options) {
        if (options && 'chunk' in options) {
            options.url = baseURL + 'postcards' + options.chunk + '.js'
            options.add = true
        }
        var success = options.success
        options.success = function(collection, response) {
            if (response.chunk_id) {
                collection.loadedChunks[response.chunk_id] = true
            }
            if (success) { success(collection, response) }
        }
        Backbone.Collection.prototype.fetch.call(this, options)
    },

    sync: function(method, model, options) {
        Backbone.sync(method, model, _.extend({
            dataType: 'jsonp',
            jsonp: false,
            jsonpCallback: 'postcardCallback' + ('chunk' in options ? options.chunk : ''),
            cache: true
        }, options))
    },

    parse: function(response) {
        return response.postcards
    },

    comparator: function(model) {
        return model instanceof Postcard ? -model.id : -model.get('chunkStart')
    }
})

PostcardRouter = Backbone.Router.extend({
    routes: {
        'view/:cardId': 'viewCard',
    },

    initialize: function(options) {
        this.zoomer = options.zoomer
        this.zoomer.on('zoom', function(cardId) {
            this.navigate('view/' + cardId)
        }, this)
        this.zoomer.on('unzoom', function(cardId) {
            this.navigate('browse', {replace: true})
        }, this)
    },

    viewCard: function(cardId) {
        this.zoomer.zoomById(Number(cardId))
    }
})

var PostcardInfoView = Backbone.View.extend({
    tagName: 'div',
    className: 'cardinfo',

    events: {
        'mouseover': 'zoomIn',
        'mouseout': 'zoomOut'
    },

    initialize: function() {
        _.bindAll(this, '_position', 'hide')
        this.options.parent.bind('showcard', this._position)
        this.options.parent.bind('hidecard', this.hide)
    },

    render: function() {
        $(this.el).append(
            this.make('a', {class: 'maplink', target: '_blank'}, [
                this.make('img', {class: 'map'})
            ]),
            this.make('span', {class: 'date'})
        )

        this.zoomOut()
        this.$('.date').text(this.model.get('date'))
        return this
    },

    hide: function() {
        $(this.el).addClass('hide')
    },

    zoomIn: function() {
        this.updateMap(8)
    },

    zoomOut: function() {
        this.updateMap(1)
    },

    updateMap: function(zoom) {
        this.$('.maplink').attr('href', mapURL({
            lat: this.model.get('latitude'),
            long: this.model.get('longitude')
        }))
        this.$('.map').attr('src', mapImageURL({
            lat: this.model.get('latitude'),
            long: this.model.get('longitude'),
            width: 85,
            height: 85,
            zoom: zoom
        }))
    },

    _position: function() {
        var parent = this.options.parent,
            image = parent.currentImage(),
            parentPos = parent.position,
            oldTarget = this.target || {left: 0, top: 0},

            // Since the parent is animating, we must calculate the final position.
            target = {
                left: parentPos.left + (parent.maxWidth - image.width) / 2 - $(this.el).outerWidth() - 10,
                top: parentPos.top + (parent.maxHeight - image.height) / 2
            }

        var distance = Math.sqrt(Math.pow(target.left - oldTarget.left, 2) + Math.pow(target.top - oldTarget.top, 2))
        if (distance > 10) {
            this.hide()
            this.$el.css(target)
            this.target = target
            setTimeout(_.bind(function() {
                $(this.el)
                    .removeClass('hide')
                    .addClass('show')
            }, this), 500)
       }
    }
})

var PostcardZoomView = Backbone.View.extend({
    tagName: 'div',
    className: 'postcard-zoombox',

    events: {
        'click .zoom': 'flip'
    },

    initialize: function() {
        this.model = this.model || this.options.parent.model

        $(this.el).append(
            this.make('div', {class: 'zoom'}, [
                this.make('img', {class: 'face front'}),
                this.make('img', {class: 'face back'}),
            ])
        )

        var info = new PostcardInfoView({model: this.model, parent: this})
        $(this.el).append(info.render().el)

        var smallImages = this.model.get('images').small
        var frontOrientation = smallImages.front.width > smallImages.front.height,
            backOrientation = smallImages.back.width > smallImages.back.height
        if (frontOrientation != backOrientation) {
            $(this.el).addClass('rotate')
        }
    },

    render: function() {
        this._resize('small')
        this._position()
        return this
    },

    currentImage: function() {
        var face = !$(this.el).is('.flipped') ? 'front' : 'back'
        return this.model.get('images')[this.size][face]
    },


    _position: function() {
        var pos = this.options.parent.$('img').offset()
        this.$('.zoom').css({
            left: pos.left - this.frontLeft,
            top: pos.top
        })
    },

    _resize: function(size, keepImages) {
        this.size = size
        var images = this.model.get('images')[size]

        // Scale and center the images.
        this.maxWidth = Math.max(images.front.width, images.back.width),
        this.maxHeight = Math.max(images.front.height, images.back.height)
        this.frontLeft = (this.maxWidth - images.front.width) / 2,
        this.frontTop = (this.maxHeight - images.front.height) / 2

        this.$('.front').attr('width', images.front.width)

        cardOffset = 
        this.$('.back')
            .attr('width', images.back.width)
            .css({
                left: -(this.maxWidth - images.front.width) / 2,
                top: (this.maxHeight - images.back.height) / 2
            })

        this.$('.zoom').css({
            width: images.front.width,
            height: images.front.height,
            marginLeft: this.frontLeft,
            marginTop: this.frontTop
        })

        if (!keepImages) {
            this.$('.front').attr('src', baseURL + images.front.filename)
            this.$('.back').attr('src', baseURL + images.back.filename)
        }
    },

    flip: function() {
        if (!this.$el.is('.zoomed')) { return }
        this.$el.toggleClass('flipped')
        this.trigger('showcard')
        return this
    },

    zoom: function() {
        var images = this.model.get('images')
        this._resize('full')
        this.position = {
            'left': ($(window).width() - this.maxWidth) / 2,
            'top': Math.max(this.$el.parent().position().top + 10,
                            $(window).scrollTop() + ($(window).height() - this.maxHeight) / 2),
        }
        this.$('.zoom').css(this.position)
        this.$el.addClass('zoomed')
        this.trigger('showcard')
        return this
    },

    unzoom: function() {
        this.trigger('hidecard')
        this.$el.removeClass('flipped zoomed')
        this._resize('small', true)
        this._position()
        this.$el.one('webkitTransitionEnd', _.bind(function() {
            this.remove()
        }, this))
    }
})

var PostcardView = Backbone.View.extend({
    tagName: 'div',
    className: 'postcard',

    events: {
        'click img': 'zoom'
    },

    render: function() {
        var thumb = this.model.get('images').small,
            front = thumb.front || {}
        $(this.el).append(
            $(this.make('img', {
                src: baseURL + front.filename,
                width: front.width,
                height: front.height
            })).css('margin-top', -front.height / 2)
        )
        return this
    },

    zoom: function() {
        this.options.zoomer.zoom(this)
    },
})

var PostcardsPlaceholderView = Backbone.View.extend({
    tagName: 'div',
    className: 'placeholder',
    perLine: 4,
    lineHeight: 215 + 2 * 4,

    render: function() {
        var grid = this.options.parent
        this.$el.css('height', Math.ceil(grid.collection.chunkSize / this.perLine) * this.lineHeight)
        return this
    }
})

var PostcardGridView = Backbone.View.extend({
    initialize: function() {
        this.collection
            .on('add', this.addOne, this)
            .on('remove', this.removeOne, this)
            .on('reset', this.addAll, this)

        this.itemViews = []
        this.placeholders = []

        _.bindAll(this, '_clickOut', '_scroll')
        $('body').bind('click', this._clickOut)
        $(window).bind('scroll', this._scroll)
    },

    addOne: function(model) {
        if (model instanceof Postcard) {
            var view = new PostcardView({model: model, zoomer: this})
        } else if (model instanceof PostcardsPlaceholder) {
            var view = new PostcardsPlaceholderView({model: model, parent: this})
            this.placeholders.push(view)
        }

        var index = this.collection.indexOf(model),
            elBefore = this.$el.children().eq(index)
        if (elBefore.length) {
            elBefore.after(view.render().el)
        } else {
            this.$el.append(view.render().el)
        }
        this.itemViews[model.id] = view
    },

    removeOne: function(model) {
        var view = this.itemViews[model.id]
        view.remove()
        this.itemViews[model.id] = null
    },

    addAll: function() {
        this.collection.each(this.addOne, this)
    },

    zoomById: function(cardId) {
        this.collection.ensureLoaded(cardId, _.bind(function() {
            var postcardView = this.itemViews[cardId]
            if (postcardView) {
                $(window).scrollTop(postcardView.$el.offset().top - $(window).height() / 2)
                this._scroll()
                this.zoom(postcardView)
            }
        }, this))
    },

    zoom: function(postcard) {
        if (!this.currentZoom || postcard.model.id != this.currentZoom.model.id) {
            this.unzoom(true)
            this.zoomScroll = $(window).scrollTop()
            this.$el.addClass('zoomed')
            this.trigger('zoom', postcard.model.id)
            var zoom = this.currentZoom = new PostcardZoomView({parent: postcard, zoomer: this})
            $('#about-postcards').append(zoom.render().el)
            _.defer(function() {
                zoom.zoom().flip()
            })
        }
    },

    unzoom: function(switching) {
        if (!switching) {
            this.$el.removeClass('zoomed')
            this.trigger('unzoom')
        }
        if (this.currentZoom) {
            this.currentZoom.unzoom()
            this.currentZoom = null
        }
    },

    _clickOut: function(ev) {
        if (this.currentZoom && !$(ev.target).closest($([this.currentZoom.el, this.currentZoom.options.parent.el])).length) {
            this.unzoom()
        }
    },

    _scroll: _.debounce(function() {
        var unzoomThreshold = 800,
            scrollTop = $(window).scrollTop()
        if (this.currentZoom && Math.abs(this.zoomScroll - scrollTop) > unzoomThreshold) {
            this.unzoom()
        }

        this.placeholders = _.reject(this.placeholders, function(placeholder) {
            var pos = placeholder.$el.offset(),
                height = placeholder.$el.height()
            if (Math.abs(scrollTop - pos.top) < height + $(window).height() ) {
                var model = placeholder.model
                this.collection.ensureLoaded(model.get('chunkStart'), _.bind(function() {
                    this.collection.remove(model)
                }, this))
                return true
            }
        }, this)
    }),
})

r.about.pages['about-postcards'] = function() {
    $('.abouttitle h1').hide()

    // FIXME var
    var postcards = new PostcardCollection,
        grid = new PostcardGridView({
            el: $('#postcards'),
            collection: postcards
        })

    var cardRouter = new PostcardRouter({zoomer: grid})
    postcards.load(function() {
        if (!Backbone.history.start()) {
            cardRouter.navigate('browse')
        }
        $('.abouttitle h1')
            .find('.count').text(postcards.totalCount).end()
            .fadeIn()
    })
}
