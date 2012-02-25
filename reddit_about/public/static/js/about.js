r.about = { pages: {} }

$(function() {
    var page = $('.content.about-page')
    if (page) {
        r.about.pages[page.attr('id')]()
    }
})
