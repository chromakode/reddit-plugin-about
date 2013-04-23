$(function() {
    var sidebarEl = $('.policy-page .doc-info')
    new scrollFixed(sidebarEl)

    var docEl = $('.policy-page .md'),
        tocEl = $('.policy-page .doc-info .toc'),
        progressBead = $('<div class="location">').appendTo(tocEl)

    var tocFor = function(el) {
        return tocEl.find('a[href$="#' + el.attr('id') + '"]')
    }

    var updateProgress = _.throttle(function() {
        var scrollTop = $(window).scrollTop(),
            scrollMax = $(document).height() - $(window).height(),
            nextHeading = $(_.find(docEl.find('h2'), function(el) {
                return $(el).offset().top >= scrollTop
            })),
            prevHeading = nextHeading.prevAll('h2').first()

        if (!nextHeading.length || scrollTop == scrollMax) {
            prevHeading = nextHeading = $('h2:last')
        }

        if (!prevHeading.length) {
            progressBead.css('top', 0)
        } else {
            var nextTop = nextHeading.offset().top,
                prevTop = prevHeading.offset().top,
                sectionPercent = (scrollTop - prevTop) / (nextTop - prevTop),
                nextToc = tocFor(nextHeading),
                prevToc = tocFor(prevHeading),
                nextTocTop = nextToc.position().top,
                prevTocTop = prevToc.position().top

            sectionPercent = r.utils.clamp(sectionPercent, 0, 1)
            var beadTop = prevTocTop + (nextTocTop - prevTocTop) * sectionPercent
            progressBead.css('top', beadTop)
        }
    }, 10)
    $(window).bind('scroll', updateProgress)
    updateProgress()

    var markFragment = function() {
        var fragmentHeading = $(document.getElementById(location.hash.substr(1)))
        if (fragmentHeading.length) {
            progressBead.css('top', tocFor(fragmentHeading).position().top)
            $(window).unbind('scroll', updateProgress)
            setTimeout(function() {
                $(window).bind('scroll', updateProgress)
            }, 100)
        }
    }
    $(window).bind('hashchange', markFragment)
    tocEl.on('click', 'a', markFragment)
    markFragment()
})
