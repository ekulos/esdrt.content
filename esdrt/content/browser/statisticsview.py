from Products.CMFCore.utils import getToolByName
from esdrt.content.reviewfolder import IReviewFolder
from five import grok
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


grok.templatedir('templates')


class StatisticsView(grok.View):
    grok.context(IReviewFolder)
    grok.name('statistics')
    grok.require('zope2.View')

    def get_countries(self):
        factory = getUtility(IVocabularyFactory,
            'esdrt.content.eea_member_states'
        )
        vocabulary = factory(self.context)
        return sorted([k for k, v in vocabulary.by_token.items()])

    def observation_status_per_country(self):
        data = []
        observations = self.get_observations()
        for country in self.get_countries():
            item = observations.get(country, {})
            item['country'] = country
            data.append(item)

        data.append(self.calculate_sum(data))
        return data

    def sum_observation(self, data, country, status):
        val = data.get(country, {}).get(status, 0)
        val += 1
        data.setdefault(country, {})
        data[country][status] = val
        return data

    def get_observations(self):
        data = {}
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='Observation'
        )
        for brain in brains:
            data = self.sum_observation(
                data,
                brain.country,
                brain.observation_status
            )

        for k, v in data.items():
            data[k]['sum'] = sum(v.values())

        return data

    def calculate_sum(self, items):
        ret = reduce(lambda x, y: dict((k, v + (y and y.get(k, 0) or 0)) for k, v in x.iteritems()), items)
        ret['country'] = 'Sum'
        return ret
