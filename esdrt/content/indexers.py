from plone.indexer import indexer
from .observation import IObservation


@indexer(IObservation)
def observation_country(context):
    return context.country


@indexer(IObservation)
def observation_crf_code(context):
    return context.crf_code


@indexer(IObservation)
def observation_ghg_source_category(context):
    return context.ghg_source_category


@indexer(IObservation)
def observation_ghg_source_sectors(context):
    return context.ghg_source_sectors


@indexer(IObservation)
def observation_status_flag(context):
    return context.status_flag
