from collections import namedtuple

TestUserDBInfo = namedtuple("TestUserDBInfo", ["id", "email", "password_digest"])
TestDataRequestInfo = namedtuple("TestDataRequestInfo", ["id", "submission_notes"])
TestAgencyInfo = namedtuple("TestAgencyInfo", ["id", "submitted_name"])
