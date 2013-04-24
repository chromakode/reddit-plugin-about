function scrollFixed(el) {
    this.$el = $(el)
    this.$standin = null
    this.origTop = this.$el.position().top
    this.onScroll()
    $(window).bind('scroll resize', _.bind(this.onScroll, this))
}
scrollFixed.prototype = {
    onScroll: function() {
        var enoughSpace = this.$el.height() < $(window).height()
        if (enoughSpace && $(window).scrollTop() > this.origTop) {
            if (!this.$standin) {
                this.$standin = $('<div>')
                    .css({
                        width: this.$el.width(),
                        height: this.$el.height()
                    })
                    .attr('class', this.$el.attr('class'))

                this.$el
                    .addClass('scroll-fixed')
                    .css({
                        position: 'fixed',
                        top: 0
                    })
                this.$el.before(this.$standin)
            }
        } else {
            if (this.$standin) {
                this.$el
                    .removeClass('scroll-fixed')
                    .css({
                        position: '',
                        top: ''
                    })
                this.$standin.remove()
                this.$standin = null
            }
        }
    }
}
