from plone import api


def grant_local_roles(context):
    """ add local roles to the groups when adding an observation
    """
    country = context.country.lower()
    sector = context.ghg_source_category_value()
    api.group.grant_roles(
        groupname='extranet-esd-ghginv-sr-%s-%s' % (sector, country),
        roles=['ReviewerPhase1'],
        obj=context,
    )
    api.group.grant_roles(
        groupname='extranet-esd-ghginv-qualityexpert-%s' % sector,
        roles=['QualityExpert'],
        obj=context,
    )
    api.group.grant_roles(
        groupname='extranet-esd-esdreview-reviewexp-%s-%s' % (sector, country),
        roles=['ReviewerPhase2'],
        obj=context,
    )
    api.group.grant_roles(
        groupname='extranet-esd-esdreview-leadreview-%s' % country,
        roles=['LeadReviewer'],
        obj=context,
    )
    api.group.grant_roles(
        groupname='extranet-esd-countries-msa-%s' % country,
        roles=['MSAuthority'],
        obj=context,
    )
