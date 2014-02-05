from five import grok
from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class MSVocabulary(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pvoc = getToolByName(context, 'portal_vocabularies')
        voc = pvoc.getVocabularyByName('eu_member_states')
        terms = []
        if voc is not None:
            for key, value in voc.getVocabularyLines():
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(key, key, value))
        return SimpleVocabulary(terms)

grok.global_utility(MSVocabulary, name=u"esdrt.content.eu_member_states")


class GHGSourceCategory(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pvoc = getToolByName(context, 'portal_vocabularies')
        voc = pvoc.getVocabularyByName('ghg_source_category')
        terms = []
        if voc is not None:
            for key, value in voc.getVocabularyLines():
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(key, key, value))
        return SimpleVocabulary(terms)

grok.global_utility(GHGSourceCategory,
    name=u"esdrt.content.ghg_source_category")


class GHGSourceSectors(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pvoc = getToolByName(context, 'portal_vocabularies')
        voc = pvoc.getVocabularyByName('ghg_source_sectors')
        terms = []
        if voc is not None:
            for key, value in voc.getVocabularyLines():
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(key, key, value))
        return SimpleVocabulary(terms)

grok.global_utility(GHGSourceSectors,
    name=u"esdrt.content.ghg_source_sectors")


class StatusFlag(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pvoc = getToolByName(context, 'portal_vocabularies')
        voc = pvoc.getVocabularyByName('status_flag')
        terms = []
        if voc is not None:
            for key, value in voc.getVocabularyLines():
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(key, key, value))
        return SimpleVocabulary(terms)

grok.global_utility(StatusFlag,
    name=u"esdrt.content.status_flag")


class CRFCode(object):
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        pvoc = getToolByName(context, 'portal_vocabularies')
        voc = pvoc.getVocabularyByName('crf_code')
        terms = []
        if voc is not None:
            for key, value in voc.getVocabularyLines():
                # create a term - the arguments are the value, the token, and
                # the title (optional)
                terms.append(SimpleVocabulary.createTerm(key, key, value))
        return SimpleVocabulary(terms)

grok.global_utility(CRFCode,
    name=u"esdrt.content.crf_code")
