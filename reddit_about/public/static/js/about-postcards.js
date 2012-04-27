var baseURL = 'http://postcards.redditstatic.com/',
    mapURL = _.template('http://maps.google.com/?q=<%= d.lat %>,<%= d.long %>'),
    mapImageURL = _.template('http://maps.googleapis.com/maps/api/staticmap?zoom=<%= d.zoom %>&size=<%= d.width %>x<%= d.height %>&sensor=false&markers=size:mid%7Ccolor:red%7C<%= d.lat %>,<%= d.long %>')

Postcard = Backbone.Model.extend({})

PostcardCollection = Backbone.Collection.extend({
    model: Postcard,
    url: baseURL + 'postcards-latest.js',
    chunkSize: null,
    loadedChunks: {},

    init: function(callback) {
        this.fetch({success: _.bind(function(collection, response) {
            this.chunkSize = this.length
            this.totalCount = response.total_postcard_count
            callback()
        }, this)})
    },

    ensureLoaded: function(cardId, callback) {
        var chunkId = Math.floor(cardId / this.chunkSize)
        if (chunkId in this.loadedChunks) {
            callback()
        } else {
            this.fetch({chunk: chunkId, add: true, success: callback})
        }
    },

    fetch: function(options) {
        if (options && 'chunk' in options) {
            options.url = baseURL + 'postcards' + options.chunk + '.js'
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
            cache: true // FIXME
        }, options))
    },

    parse: function(response) {
        return response.postcards
    },

    comparator: function(model) {
        return -model.id
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
        'click': 'zoom'
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

var PostcardGridView = GridView.extend({
    initialize: function() {
        GridView.prototype.initialize.apply(this)

        _.bindAll(this, '_clickOut', '_scroll')
        $('body').bind('click', this._clickOut)
        $(window).bind('scroll', this._scroll)
    },

    createItemView: function(model) {
        var view = new PostcardView({model: model, zoomer: this})
        this.$el.append(view.render().el)
        return view
    },

    addAll: function() {
        this.collection.each(this.addOne, this)
    },

    zoomById: function(cardId) {
        this.collection.ensureLoaded(cardId, _.bind(function() {
            _.defer(_.bind(function() {
                var postcardView = this.itemViews[cardId]
                if (postcardView) {
                    $(window).scrollTop(postcardView.$el.offset().top - $(window).height() / 2)
                    this.zoom(postcardView)
                }
            }, this))
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

    _scroll: function() {
        if (this.currentZoom
                && Math.abs(this.zoomScroll - $(window).scrollTop()) > 800) {
            this.unzoom()
        }
    },
})

r.about.pages['about-postcards'] = function() {
    $('.abouttitle h1').hide()

    postcards = new PostcardCollection,
        grid = new PostcardGridView({
            el: $('#postcards'),
            collection: postcards
        })

    var cardRouter = new PostcardRouter({zoomer: grid})
    postcards.init(function() {
        if (!Backbone.history.start()) {
            cardRouter.navigate('browse')
        }
        $('.abouttitle h1')
            .find('.count').text(postcards.totalCount).end()
            .fadeIn()
    })
}
