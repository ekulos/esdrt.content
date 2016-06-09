from Products.CMFCore.utils import getToolByName
import transaction

PROFILE_ID = 'profile-esdrt.content:default'


def upgrade(context, logger=None):
    if logger is None:
        from logging import getLogger
        logger = getLogger('esdrt.content.upgrades.46_47')

    update_ploneregistry(context, logger)
    logger.info('Upgrade steps executed')


def update_ploneregistry(context, logger):
    setup = getToolByName(context, 'portal_setup')
    logger.info('Update plone registry')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
    transaction.commit()
