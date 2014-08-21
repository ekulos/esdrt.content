from esdrt.content.reviewfolder import IReviewFolder
from five import grok
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

import random

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

    def observation_status(self):
        data = []
        for country in self.get_countries():
            item = self.get_observation_status_per_country(country)
            data.append(item)

        data.append(self.calculate_sum(data))
        return data

    def get_observation_status_per_country(self, country):
        draft = random.randint(0, 10)
        open = random.randint(0, 10)
        conclusion = random.randint(0, 10)
        finished = random.randint(0, 10)
        item = dict(
            country=country,
            draft=draft,
            open=open,
            conclusion=conclusion,
            finished=finished,
            sum=draft + open + conclusion + finished,
        )
        return item

    def calculate_sum(self, items):
        ret = reduce(lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()), items)
        ret['country'] = 'Sum'
        return ret

