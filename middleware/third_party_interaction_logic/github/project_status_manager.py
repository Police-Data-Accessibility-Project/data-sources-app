class ProjectStatusManager:
    def __init__(self, options: dict):
        self.d = {}
        for option in options:
            id_ = option["id"]
            name = option["name"]
            self.d[name] = id_

    def get_id(self, name):
        return self.d[name]

    def get_all_ids(self):
        return list(self.d.values())
