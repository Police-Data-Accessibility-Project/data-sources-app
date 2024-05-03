import uuid
from collections import namedtuple


TestTokenInsert = namedtuple("TestTokenInsert", ["id", "email", "token"])
TestUser = namedtuple("TestUser", ["id", "email", "password_hash"])

def insert_test_agencies_and_sources(cursor):
    """

    :param cursor:
    :return:
    """

    cursor.execute(
        """
        INSERT INTO
        PUBLIC.DATA_SOURCES (
            airtable_uid,
            NAME,
            DESCRIPTION,
            RECORD_TYPE,
            SOURCE_URL,
            APPROVAL_STATUS,
            URL_STATUS
        )
        VALUES
        ('SOURCE_UID_1','Source 1','Description of src1','Type A','http://src1.com','approved','available'),
        ('SOURCE_UID_2','Source 2','Description of src2','Type B','http://src2.com','approved','available'),
        ('SOURCE_UID_3','Source 3', 'Description of src3', 'Type C', 'http://src3.com', 'pending', 'available');
        
        INSERT INTO public.agencies (airtable_uid, name, municipality, state_iso, county_name, count_data_sources)
        VALUES 
            ('Agency_UID_1', 'Agency A', 'City A', 'CA', 'County X', 3),
            ('Agency_UID_2', 'Agency B', 'City B', 'NY', 'County Y', 2),
            ('Agency_UID_3', 'Agency C', 'City C', 'TX', 'County Z', 1);
            
        INSERT INTO public.agency_source_link (airtable_uid, agency_described_linked_uid)
        VALUES 
            ('SOURCE_UID_1', 'Agency_UID_1'),
            ('SOURCE_UID_2', 'Agency_UID_2'),
            ('SOURCE_UID_3', 'Agency_UID_3');
        """
    )


def get_reset_tokens_for_email(db_cursor, reset_token_insert):
    db_cursor.execute(
        """
        SELECT email from RESET_TOKENS where email = %s
        """,
        (reset_token_insert.email,),
    )
    results = db_cursor.fetchall()
    return results




def create_reset_token(cursor) -> TestTokenInsert:
    user = create_test_user(cursor)
    token = uuid.uuid4().hex
    cursor.execute(
        """
        INSERT INTO reset_tokens(email, token) 
        VALUES (%s, %s)
        RETURNING id
        """,
        (user.email, token),
    )
    id = cursor.fetchone()[0]
    return TestTokenInsert(id=id, email=user.email, token=token)


def create_test_user(
    cursor,
    email="example@example.com",
    password_hash="hashed_password_here",
    api_key="api_key_here",
    role=None,
) -> TestUser:
    """
    Creates test user and returns the id of the test user
    :param cursor:
    :return: user id
    """
    cursor.execute(
        """
        INSERT INTO users (email, password_digest, api_key, role)
        VALUES
        (%s, %s, %s, %s)
        RETURNING id;
        """,
        (email, password_hash, api_key, role),
    )
    return TestUser(
        id=cursor.fetchone()[0],
        email=email,
        password_hash=password_hash,
    )
