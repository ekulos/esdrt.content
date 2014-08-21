from esdrt.content.reviewfolder import IReviewFolder
from five import grok

grok.templatedir('templates')


class StatisticsView(grok.View):
    grok.context(IReviewFolder)
    grok.name('statistics')
    grok.require('zope2.View')
