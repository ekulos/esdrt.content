from zope.globalrequest import getRequest
from Products.CMFCore.utils import getToolByName

PROFILE_ID = 'profile-esdrt.content:default'


def upgrade(context, logger=None):
    if logger is None:
        from logging import getLogger
        logger = getLogger('esdrt.content.upgrades.38_39')
    reindex_index(context, logger)
    logger.info('Upgrade steps executed')


def reindex_index(context, logger):
    logger.info('Reindexing indexes')
    catalog = getToolByName(context, 'portal_catalog')
    catalog.reindexIndex(name='observation_sent_to_msc',
        REQUEST=getRequest())
    catalog.reindexIndex(name='observation_sent_to_mse',
        REQUEST=getRequest())

