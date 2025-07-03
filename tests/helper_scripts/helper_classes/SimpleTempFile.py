import os
import tempfile


class SimpleTempFile:
    def __init__(self, suffix: str = ".csv"):
        self.suffix = suffix
        self.temp_file = None

    def __enter__(self):
        self.temp_file = tempfile.NamedTemporaryFile(
            mode="w+", encoding="utf-8", suffix=self.suffix, delete=False
        )
        return self.temp_file

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.temp_file.close()
            os.unlink(self.temp_file.name)
        except Exception as e:
            print(f"Error cleaning up temporary file {self.temp_file.name}: {e}")
