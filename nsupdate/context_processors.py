# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

MAX_IP_AGE = 180  # seconds


def add_settings(request):
    context = {}
    context['WWW_HOST'] = settings.WWW_HOST
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    return context


def remove_stale_ips(request):
    """
    Check the session if there are stale IPs and if so, remove them.
    """
    # XXX is a context processor is the right place for this?
    s = request.session
    t_now = now()
    for key in ['ipv4', 'ipv6', ]:
        timestamp_key = "%s_timestamp" % key
        try:
            timestamp = s[timestamp_key]
        except KeyError:
            # should be always there, initialize it:
            s[key] = ''
            s[timestamp_key] = t_now
        else:
            try:
                stale = timestamp + timedelta(seconds=MAX_IP_AGE) < t_now
            except (ValueError, TypeError):
                # invalid timestamp in session
                del s[timestamp_key]
            else:
                if stale:
                    logger.debug("ts: %s now: %s - killing stale %s (was: %s)" % (timestamp, t_now, key, s[key]))
                    # kill the IP, it is not up-to-date any more
                    # note: it is used to fill form fields, so set it to empty string
                    s[key] = ''
                    # update the timestamp, so we can retry after a while
                    s[timestamp_key] = t_now
    return {}