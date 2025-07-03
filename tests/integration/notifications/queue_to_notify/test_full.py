"""
Test the full process of events in the event queue being sent to users as notifications.

When events are added to their respective queues,
they should be sent out to users who are subscribed
to an encompassing location.

In the case of data sources (but not data requests),
the entity should be sent out only to users subscribed to that record type

These same events should not be sent to users a second time.
"""
