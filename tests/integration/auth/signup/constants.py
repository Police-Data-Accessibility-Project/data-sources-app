from db.enums import UserCapacityEnum

PATCH_ROOT = "endpoints.instantiations.auth_.signup.middleware"
TEST_USER_CAPACITIES = [
    UserCapacityEnum.POLICE,
    UserCapacityEnum.COMMUNITY_MEMBER,
 ]