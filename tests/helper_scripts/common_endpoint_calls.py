"""
This contains common endpoint calls which are used across
multiple integration tests
"""

from collections import namedtuple

CreatedDataSource = namedtuple("CreatedDataSource", ["id", "name", "url"])
