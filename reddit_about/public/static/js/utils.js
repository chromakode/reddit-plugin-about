function scrollFixed(el) {
    this.$el = $(el)
    this.origTop = this.$el.position().top
    this.onScroll()
    $(window).scroll(_.bind(this.onScroll, this))
}
scrollFixed.prototype = {
    onScroll: function() {
        if ($(window).scrollTop() > this.origTop) {
            this.$el.css({
                position: 'fixed',
                top: 0
            })
        } else {
            this.$el.css({
                position: 'static'
            })
        }
    }
}
