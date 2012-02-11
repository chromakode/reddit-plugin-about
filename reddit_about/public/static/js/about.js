slideshowImages = new Backbone.Collection

AboutSlideshowView = SlideshowView.extend({
    interval: 10*1000,
    render: function() {
        SlideshowView.prototype.render.apply(this)
        var image = this.collection.at(this.index)
        this.$('.title')
            .attr('href', image.get('url'))
            .text(image.get('title'))
        this.$('.author')
            .attr('href', image.get('author_url'))
            .text(image.get('author'))
        this.$('.user')
            .attr('href', image.get('via_url'))
            .text(image.get('via'))
        this.$('.comments')
            .attr('class', image.get('comment_class'))
            .addClass('comments')
            .text(image.get('comment_label'))
        return this
    }
})

$(function() {
    var slideshow = new AboutSlideshowView({
        el: $('.about-page #slideshow'),
        collection: slideshowImages
    }).play()
})
