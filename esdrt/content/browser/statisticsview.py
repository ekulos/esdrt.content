from Products.CMFCore.utils import getToolByName
from esdrt.content.reviewfolder import IReviewFolder
from five import grok
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import itertools
import copy
import operator


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

    def _generic_getter(self, items, key, value, columns=[], filter_fun=None):
        """
         Generic function to get items for later rendering.
         Parameters:
          - Key: name of the field that will be shown in files
          - Value: name of the field that will be counted
          - Columns: values of the 'value' field that will be counted and shown
          - obs_filter: a function returning if a given observation should be
                        included on the count or not.

        """
        data = []
        items = {}
        # Get the items, filtered if needed
        filted_items = filter(filter_fun, items)
        # Set sorting and grouping key into a function
        getkey = operator.itemgetter(key)
        filted_items.sort(key=getkey)
        # get observations grouped by the value of the key
        for gkey, item in itertools.groupby(filted_items, key=getkey):
            val = items.get(gkey, [])
            val.extend([o.get(value) for o in item])
            items[gkey] = val

        # Count how many observations are per-each of the columns
        for gkey, values in items.items():
            item = {}
            for column in columns:
                item[column] = values.count(column)

            # Calculate the sum
            val = sum(item.values())
            item['sum'] = val
            item[key] = gkey
            data.append(item)

        # Calculate the final sum
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

    def _generic_observation(self, key, value, columns=[], filter_fun=None):
        return self._generic_getter(
            self.observations,
            key,
            value,
            columns,
            filter_fun,
        )

    def _generic_question(self, key, value, columns=[], filter_fun=None):
        return self._generic_getter(
            self.questions,
            key,
            value,
            columns,
            filter_fun,
        )

    def get_sectors(self):
        return self.get_vocabulary_values('esdrt.content.ghg_source_sectors')

    def observation_status_per_country(self):
        return self._generic_observation(
            key='country',
            value='status',
            columns=['open', 'draft', 'closed', 'conclusions']
        )

    def observation_status_per_sector(self):
        return self._generic_observation(
            key='sector',
            value='status',
            columns=['open', 'draft', 'closed', 'conclusions']
        )

    def question_status_per_country(self):
        return self._generic_question(
            key='country',
            value='status',
            columns='esdrt.content.eea_member_states'
        )

    def question_status_per_sector(self):
        return self._generic_question(
            key='sector',
            value='status',
            columns='esdrt.content.ghg_source_sectors'
        )

    def observation_highlights_pgf(self):
        return self._generic_observation(
            key='country',
            value='sector',
            columns=self.get_sectors(),
            filter_fun=lambda x: 'pgf' in x.get('highlight', []),
        )

    def observation_highlights_psi(self):
        return self._generic_observation(
            key='country',
            value='sector',
            columns=self.get_sectors(),
            filter_fun=lambda x: 'psi' in x.get('highlight', []),
        )

    def observation_highlights_ptc(self):
        return self._generic_observation(
            key='country',
            value='sector',
            columns=self.get_sectors(),
            filter_fun=lambda x: 'ptc' in x.get('highlight', []),
        )
