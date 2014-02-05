from datetime import datetime
from esdrt.content import MessageFactory as _
from five import grok
from plone.app.textfield import RichText
from plone.directives import dexterity, form
from plone.directives.form import default_value
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


# Interface class; used to define content-type schema.
class IObservation(form.Schema, IImageScaleTraversable):
    """
    New review observation
    """
    country = schema.Choice(
        title=_(u"Country"),
        vocabulary='esdrt.content.eu_member_states',

    )

    year = schema.Int(
        title=_(u'Observation year'),
    )

    crf_code = schema.Choice(
        title=_(u"CRF Code"),
        vocabulary='esdrt.content.crf_code',

    )

    ghg_source_category = schema.Choice(
        title=_(u"GHG Source Category"),
        vocabulary='esdrt.content.ghg_source_category',

    )

    ghg_source_sectors = schema.Choice(
        title=_(u"GHG Source Sectors"),
        vocabulary='esdrt.content.ghg_source_sectors',

    )

    status_flag = schema.Choice(
        title=_(u"Status Flag"),
        vocabulary='esdrt.content.status_flag',

    )


@default_value(field=IObservation['year'])
def year_default_value(data):
    return datetime.now().year - 1


class Observation(dexterity.Container):
    grok.implements(IObservation)
    # Add your class methods and properties here

    def country_value(self):
        return self._vocabulary_value('esdrt.content.eu_member_states',
            self.country
        )

    def crf_code_value(self):
        return self._vocabulary_value('esdrt.content.crf_code',
            self.crf_code
        )

    def ghg_source_category_value(self):
        return self._vocabulary_value('esdrt.content.ghg_source_category',
            self.ghg_source_category
        )

    def ghg_source_sectors_value(self):
        return self._vocabulary_value('esdrt.content.ghg_source_sectors',
            self.ghg_source_sectors
        )

    def status_flag_value(self):
        return self._vocabulary_value('esdrt.content.status_flag',
            self.status_flag
        )

    def _vocabulary_value(self, vocabulary, term):
        vocab_factory = getUtility(IVocabularyFactory, name=vocabulary)
        vocabulary = vocab_factory(self)
        value = vocabulary.getTerm(term)
        return value.title

# View class
# The view will automatically use a similarly named template in
# templates called observationview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type

grok.templatedir('templates')


class ObservationView(grok.View):
    grok.context(IObservation)
    grok.require('zope2.View')
    grok.name('view')
