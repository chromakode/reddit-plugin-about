r.about = { pages: {} }

_.extend(_.templateSettings, {
    variable: 'd'
})

$(function() {
    var page = $('.content.about-page')
    if (page) {
        r.about.pages[page.attr('id')]()
    }
})
