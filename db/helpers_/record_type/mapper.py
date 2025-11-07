from db.helpers_.record_type.mapping import RecordTypeMapping
from middleware.enums import RecordTypesEnum
from utilities.enums import RecordCategoryEnum


class RecordTypeMapper:

    def __init__(
        self,
        mappings: list[RecordTypeMapping]
    ):
        self._rt_id_to_record_type: dict[int, RecordTypesEnum] = {}
        self._record_type_to_rt_id: dict[RecordTypesEnum, int] = {}
        self._rc_id_to_category: dict[int, RecordCategoryEnum] = {}
        self._category_to_rc_id: dict[RecordCategoryEnum, int] = {}

        # Populate mappings
        for mapping in mappings:
            self._rt_id_to_record_type[mapping.record_type_id] = mapping.record_type
            self._record_type_to_rt_id[mapping.record_type] = mapping.record_type_id
            self._rc_id_to_category[mapping.record_category_id] = mapping.record_category
            self._category_to_rc_id[mapping.record_category] = mapping.record_category_id

    def get_record_type_id_by_record_type(self, record_type: RecordTypesEnum) -> int:
        return self._record_type_to_rt_id[record_type]

    def get_record_type_by_record_type_id(self, record_type_id: int) -> RecordTypesEnum:
        return self._rt_id_to_record_type[record_type_id]

    def get_record_category_id_by_record_category(self, record_category: RecordCategoryEnum) -> int:
        return self._category_to_rc_id[record_category]

    def get_record_category_by_record_category_id(self, record_category_id: int) -> RecordCategoryEnum:
        return self._rc_id_to_category[record_category_id]
