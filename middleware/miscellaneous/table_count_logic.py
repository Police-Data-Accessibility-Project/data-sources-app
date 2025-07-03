class TableCountReference:
    def __init__(self, table, count, modified=False):
        self.table = table
        self.count = count
        self.modified = modified

    def __str__(self):
        return f"{self.table}: {self.count}"

    def update_count(self, count):
        self.count = count
        self.modified = True

    def is_modified(self):
        return self.modified


class TableCountReferenceManager:
    def __init__(self):
        self.d: dict[str, TableCountReference] = {}

    def add_table_count(self, table_name: str, count: int, is_new: bool = False):
        if table_name in self.d:
            self.d[table_name].update_count(count)
            return
        self.d[table_name] = TableCountReference(table_name, count, modified=is_new)

    def get_table_count(self, table_name: str) -> int | None:
        if table_name not in self.d:
            return None
        tcr = self.d[table_name]
        return tcr.count

    def get_modified_table_references(self) -> list[TableCountReference]:
        return [tcr for tcr in self.d.values() if tcr.is_modified()]

    def get_table_references(self) -> list[TableCountReference]:
        return list(self.d.values())
