import os


class CalibreLibrary:
    def __init__(self, path: str):
        self._path = path

    def list_all_opf(self):
        file_paths = []
        for dirpath, dirnames, filenames in os.walk(self._path):
            for filename in filenames:
                if filename == 'metadata.opf':
                    file_path = os.path.join(dirpath, filename)
                    file_paths.append(file_path)
        return file_paths



