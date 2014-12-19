from Products.CMFDiffTool import dexteritydiff

dexteritydiff.EXCLUDED_FIELDS = (
    'modification_date',
    'changeNote',
    'ghg_estimations'
)
from logging import getLogger
log = getLogger(__name__)
log.info('Patching difftool excluded fields to add ghg_estimations')
