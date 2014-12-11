def get_category_ldap_from_crf_code(value):
    """ get the CRF category this CRF Code matches
        According to the rules previously set
        for LDAP Matching
    """
    return u'sector1'


def get_category_value_from_crf_code(value):
    """ get the CRF category value to show it in the observation metadata """
    return u'Sector Value'
