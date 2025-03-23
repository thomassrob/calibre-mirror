import os
from pathlib import Path

from calibre_library.calibre_library import CalibreLibrary
from opf_parser.opf_parser import OPFParser

LIBRARY_PATH = '/Volumes/Scratch/calibre-staging-library-test'
MIRROR_PATH = '/Volumes/Scratch/test-mirror'

def main():
    calibre = CalibreLibrary(LIBRARY_PATH)
    for file in calibre.list_all_opf():
        file_path = Path(file)
        parser = OPFParser(file_path.read_text())
        matched_format = ''
        parent_dir = ''
        if parser.in_ext_lib('test-ext-lib'):
            parent_dir = os.path.dirname(file)
            for book in os.listdir(parent_dir):
                if book.endswith('.cbz'):
                    matched_format = book

            title = parser.get_title()
            series = parser.get_series()
            source_path = os.path.join(parent_dir, matched_format)
            parent_link = os.path.join(MIRROR_PATH, series, title)
            link_path = os.path.join(parent_link, matched_format)
            os.makedirs(parent_link, exist_ok=True)
            print(f'Linking {source_path} to {link_path}')
            os.link(source_path, link_path)


if __name__ == "__main__":
    main()
