from plone.app.discussion.interfaces import IConversation
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
    return context.ghg_source_category_value()


@indexer(IObservation)
def observation_ghg_source_sectors(context):
    return context.ghg_source_sectors_value()


@indexer(IObservation)
def observation_status_flag(context):
    return context.status_flag

@indexer(IObservation)
def observation_year(context):
    return context.year

@indexer(IObservation)
def observation_review_year(context):
    return context.review_year

@indexer(IObservation)
def last_question_reply_number(context):
    questions = context.values(['Question'])
    replynum = 0
    if questions:
        comments = questions[0].values(['Comment'])
        if comments:
            last = comments[-1]
            disc = IConversation(last)
            return disc.total_comments

    return replynum


@indexer(IObservation)
def last_answer_reply_number(context):
    questions = context.values(['Question'])
    replynum = 0
    if questions:
        comments = questions[0].values(['CommentAnswer'])
        if comments:
            last = comments[-1]
            disc = IConversation(last)
            return disc.total_comments

    return replynum


@indexer(IObservation)
def conclusion1_reply_number(context):
    replynum = 0
    conclusions = context.values(['Conclusion'])
    if conclusions:
        conclusion = conclusions[0]
        disc = IConversation(conclusion)
        return disc.total_comments

    return replynum


@indexer(IObservation)
def conclusion2_reply_number(context):
    replynum = 0
    conclusions = context.values(['ConclusionsPhase2'])
    if conclusions:
        conclusion = conclusions[0]
        disc = IConversation(conclusion)
        return disc.total_comments

    return replynum