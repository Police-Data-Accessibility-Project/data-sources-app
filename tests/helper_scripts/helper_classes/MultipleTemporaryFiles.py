import os
import tempfile


class MultipleTemporaryFiles:
    def __init__(self, suffixes: list[str], mode="w+", encoding="utf-8", delete=False):
        if not isinstance(suffixes, list) or len(suffixes) == 0:
            raise ValueError("Suffixes must be a non-empty list.")

        self.suffixes = suffixes
        self.mode = mode
        self.encoding = encoding
        self.delete = delete
        self.temp_files = []

    def __enter__(self):
        # Create temporary files with unique suffixes
        for suffix in self.suffixes:
            temp_file = tempfile.NamedTemporaryFile(
                mode=self.mode,
                encoding=self.encoding,
                suffix=suffix,
                delete=self.delete,
            )
            self.temp_files.append(temp_file)
        return self.temp_files

    def __exit__(self, exc_type, exc_value, traceback):
        for temp_file in self.temp_files:
            try:
                temp_file.close()
                if self.delete and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception as e:
                print(f"Error cleaning up temporary file {temp_file.name}: {e}")
