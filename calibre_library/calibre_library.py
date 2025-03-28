import os


class CalibreLibrary:
    def __init__(self, path: str):
        self._path = path

    def list_all_opf(self):
        print(f'Looking for opf files in {self._path}')

        file_paths = []
        for dirpath, dirnames, filenames in os.walk(self._path):
            for filename in filenames:
                if filename == 'metadata.opf':
                    file_path = os.path.join(dirpath, filename)
                    file_paths.append(file_path)
                    print(f'Found opf: {file_path}')
        print (f'Done looking for opf files in {self._path}')
        return file_paths



