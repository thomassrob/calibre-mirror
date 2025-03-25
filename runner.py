import os
from pathlib import Path

from calibre_library.calibre_library import CalibreLibrary
from config_reader import ConfigReader
from opf_parser.opf_parser import OPFParser

LIBRARY_PATH = '/Volumes/Scratch/calibre-staging-library-test-2'
MIRROR_PATH = '/Volumes/Scratch/test-mirror'
EXT_LIB_NAME = 'test-ext-lib'
DRY_RUN = True

CONFIG_PATH = './config.yaml'


def main():
    config = ConfigReader(CONFIG_PATH).config
    lib_path = config.get('library_path', LIBRARY_PATH)
    calibre = CalibreLibrary(lib_path)
    for file in calibre.list_all_opf():
        file_path = Path(file)
        parser = OPFParser(file_path.read_text())
        matched_format = ''
        if parser.in_ext_lib(config.get('ext_lib_name', EXT_LIB_NAME)):
            parent_dir = os.path.dirname(file)
            for book in os.listdir(parent_dir):
                if book.endswith('.cbz'):
                    print(f'Found {book}')
                    matched_format = book
            if matched_format is not None:
                title = parser.get_title()
                series = parser.get_series()
                source_path = os.path.join(parent_dir, matched_format)
                parent_link = os.path.join(config.get('mirror_path', MIRROR_PATH), series if series is not None else title)
                link_path = os.path.join(parent_link, matched_format)
                os.makedirs(parent_link, exist_ok=True)
                if not DRY_RUN:
                    print(f'Linking {source_path} to {link_path}')
                    os.link(source_path, link_path)
                else:
                    print(f'<DRYRUN>Linking {source_path} to {link_path}')


if __name__ == "__main__":
    main()
