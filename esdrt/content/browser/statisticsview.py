from Products.CMFCore.utils import getToolByName
from esdrt.content.reviewfolder import IReviewFolder
from five import grok
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import itertools
import copy


grok.templatedir('templates')


class StatisticsView(grok.View):
    grok.context(IReviewFolder)
    grok.name('statistics')
    grok.require('zope2.View')

    def update(self):
        self.observations = self.get_all_observations()
        self.questions = self.get_all_questions()

    def get_all_observations(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='Observation',
            path='/'.join(self.context.getPhysicalPath())
        )
        data = []
        for brain in brains:
            item = dict(
                country=brain.country,
                status=brain.observation_status,
                sector=brain.get_ghg_source_sectors,
                highlight=brain.get_highlight,
            )
            data.append(item)
        return data

    def get_all_questions(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            portal_type='Question',
            path='/'.join(self.context.getPhysicalPath())
        )
        data = []
        for brain in brains:
            item = dict(
                country=brain.country,
                status=brain.observation_status,
                sector=brain.get_ghg_source_sectors,
            )
            data.append(item)
        return data

    def get_vocabulary_values(self, name):
        try:
            factory = getUtility(IVocabularyFactory, name)
            vocabulary = factory(self.context)
            return sorted([k for k, v in vocabulary.by_token.items()])
        except:
            return []

    def observation_status_per_country(self):
        return self._generic_observation(
            key='country',
            value='status',
            vals=['open', 'draft', 'closed', 'conclusion']
        )

    def observation_status_per_sector(self):
        return self._generic_observation(
            key='sector',
            value='status',
            vals=['open', 'draft', 'closed', 'conclusion']
        )

    def _generic_observation(self, key='country', value='status', vals=[], obs_filter=None):
        data = []
        items = {}
        observations = filter(obs_filter, self.observations)
        for gkey, observation in itertools.groupby(observations, lambda x: x.get(key)):
            val = items.get(gkey, [])
            val.extend([o.get(value) for o in observation])
            items[gkey] = val

        for gkey, values in items.items():
            item = {}
            for val in vals:
                item[val] = values.count(val)

            val = sum(item.values())
            item['sum'] = val
            item[key] = gkey
            data.append(item)

        datasum = self.calculate_sum(data, key)
        if datasum is not None:
            data.append(datasum)
        return data

    def calculate_sum(self, items, key):
        if items:
            ret = copy.copy(reduce(lambda x, y: dict((k, v + (y and y.get(k, 0) or 0)) for k, v in x.iteritems()), copy.copy(items)))
            ret[key] = 'Sum'
            return ret
        return None

    def question_status_per_country(self):
        return self._generic_question(
            key='country',
            value='status',
            vocabulary='esdrt.content.eea_member_states'
        )

    def question_status_per_sector(self):
        return self._generic_question(
            key='sector',
            value='status',
            vocabulary='esdrt.content.ghg_source_sectors'
        )

    def _generic_question(self, key, value, vocabulary):
        data = []
        items = {}
        for gkey, question in itertools.groupby(self.questions, lambda x: x.get(key)):
            val = items.get(gkey, [])
            val.extend([o.get(value) for o in question])
            items[gkey] = val

        for gkey, values in items.items():
            item = dict(
                open=values.count('open'),
                draft=values.count('draft'),
                closed=values.count('closed'),
                conclusion=values.count('conclusion'),
            )
            val = sum(item.values())
            item['sum'] = val
            item[key] = gkey
            data.append(item)

        datasum = self.calculate_sum(data, key)
        data.append(datasum)
        return data

    def get_sectors(self):
        return self.get_vocabulary_values('esdrt.content.ghg_source_sectors')

    def observation_highlights_pgf(self):
        return self._generic_observation(
            key='country',
            value='sector',
            vals=self.get_sectors(),
            obs_filter=lambda x: 'pgf' in x.get('highlight', []),
        )

    def observation_highlights_psi(self):
        return self._generic_observation(
            key='country',
            value='sector',
            vals=self.get_sectors(),
            obs_filter=lambda x: 'psi' in x.get('highlight', []),
        )

    def observation_highlights_ptc(self):
        return self._generic_observation(
            key='country',
            value='sector',
            vals=self.get_sectors(),
            obs_filter=lambda x: 'ptc' in x.get('highlight', []),
        )

