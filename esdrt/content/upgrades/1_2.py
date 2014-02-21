from Products.CMFCore.utils import getToolByName


PROFILE_ID = 'profile-esdrt.content:default'


def upgrade(context, logger=None):
    if logger is None:
        from logging import getLogger
        logger = getLogger('esdrt.content.upgrades.1_2')

    upgrade_diff_tool(context, logger)
    enable_atd_spellchecker(context, logger)
    logger.info('Upgrade step executed')


def upgrade_diff_tool(context, logger):
    # Re-run profile installation
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'difftool')
    logger.info('Upgraded Diff Tool')


def enable_atd_spellchecker(context, logger):
    tinymce = getToolByName(context, 'portal_tinymce')
    tinymce.libraries_spellchecker_choice = 'AtD'
    tinymce.libraries_atd_service_url = 'service.afterthedeadline.com'
    logger.info('Enable AtD spellcheking plugin')
