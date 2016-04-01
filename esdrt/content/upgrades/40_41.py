from Products.CMFCore.utils import getToolByName


PROFILE_ID = 'profile-esdrt.content:default'


def upgrade(context, logger=None):
    if logger is None:
        from logging import getLogger
        logger = getLogger('esdrt.content.upgrades.40_41')

    catalog_metadata(context, logger)
    logger.info('Upgrade steps executed')


def catalog_metadata(context, logger):
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    logger.info('Reindexing')
    catalog.clearFindAndRebuild()
