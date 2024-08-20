import psycopg
from psycopg import sql


class TestDataGenerator:
    """
    A class for generating test data.
    """

    def __init__(self, cursor: psycopg.cursor):
        self.cursor = cursor
        self.savepoint = None

    def build_savepoint(self, savepoint_name: str = "test_savepoint"):
        # Build savepoint using SQL composed
        raw_query = f"SAVEPOINT {savepoint_name}"
        sql_query = sql.SQL(raw_query).format(
            savepoint_name=sql.Identifier(savepoint_name)
        )
        self.cursor.execute(sql_query)
        self.savepoint = savepoint_name

    def rollback_savepoint(self):
        raw_query = f"ROLLBACK TO SAVEPOINT {self.savepoint}"
        sql_query = sql.SQL(raw_query).format(
            savepoint_name=sql.Identifier(self.savepoint)
        )
        self.cursor.execute(sql_query)

    def build_xylonslvania(self):
        """
        Builds xylonsylvania, a test environment complete with:
        a test state of Xylonsylvania
        test counties
        test agencies
        and test data sources
        :return:
        """
        self.cursor.execute(
            """
            INSERT INTO state_names (state_iso, state_name) 
            VALUES ('XY', 'Xylonsylvania')
            ON CONFLICT DO NOTHING;
            
            INSERT INTO counties (fips, name, state_iso) 
            VALUES 
            ('12345', 'Arxylodon', 'XY'),
            ('54321', 'Qtzylan', 'XY')
            ON CONFLICT DO NOTHING;
            
            INSERT INTO agencies (name, airtable_uid, municipality, state_iso, county_fips, county_name) 
            VALUES 
            ('Xylodammerung Police Agency', 'XY_SOURCE_UID', 'Xylodammerung', 'XY', '12345', 'Arxylodon'),
            ('Byrgzipal Municipal Jail', 'XY_JAIL_UID', 'Bryrgzipal', 'XY', '12345', 'Arxylodon'),
            ('Qtzylschlitzl Police Agency', 'QT_SOURCE_UID', 'Qtzylschlitzl', 'XY', '54321', 'Qtzylan'),
            ('Fyntlitzhon Jail', 'QT_JAIL_UID', 'Fyntlitzhon', 'XY', '54321', 'Qtzylan')
            ON CONFLICT DO NOTHING;
            
            INSERT INTO data_sources (airtable_uid, name, record_type, approval_status, url_status) 
            VALUES 
            ('XY_SOURCE_UID_001', 'Xylodammerung Police Department Stops', 'Stops', 'approved', 'ok'),
            ('XY_SOURCE_UID_002', 'Xylodammerung Police Department Court Case Access', 'Court Cases', 'approved', 'ok'),
            ('XY_SOURCE_UID_003', 'Byrgzipal Jail Incarceration Records', 'Court Cases', 'approved', 'ok'),
            ('XY_SOURCE_UID_004', 'Byrgzipal Jail Local Jail Inmate Roster', 'Incarceration Records', 'approved', 'ok'),
            ('QT_SOURCE_UID_001', 'Qtzylschlitzl Police Department Stops', 'Stops', 'approved', 'ok'),
            ('QT_SOURCE_UID_002', 'Qtzylschlitzl Police Department Court Case Access', 'Court Cases', 'approved', 'ok'),
            ('QT_SOURCE_UID_003', 'Fyntlitzhon Jail Incarceration Records', 'Court Cases', 'approved', 'ok'),
            ('QT_SOURCE_UID_004', 'Fyntlitzhon Jail Local Jail Inmate Roster', 'Incarceration Records', 'approved', 'ok')
            ON CONFLICT DO NOTHING;
            
            INSERT INTO agency_source_link (agency_described_linked_uid, airtable_uid) 
            VALUES 
            ('XY_SOURCE_UID', 'XY_SOURCE_UID_001'),
            ('XY_SOURCE_UID', 'XY_SOURCE_UID_002'),
            ('XY_JAIL_UID', 'XY_SOURCE_UID_003'),
            ('XY_JAIL_UID', 'XY_SOURCE_UID_004'),
            ('QT_SOURCE_UID', 'QT_SOURCE_UID_001'),
            ('QT_SOURCE_UID', 'QT_SOURCE_UID_002'),
            ('QT_JAIL_UID', 'QT_SOURCE_UID_003'),
            ('QT_JAIL_UID', 'QT_SOURCE_UID_004')
            ON CONFLICT DO NOTHING;
            
            UPDATE data_sources ds
            SET record_type_id = rt.id
            FROM record_types rt
            WHERE ds.record_type = rt.name;

        
        """
        )
