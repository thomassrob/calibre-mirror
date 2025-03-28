import os
from pathlib import Path

from calibre_library.calibre_library import CalibreLibrary
from config_reader import ConfigReader
from opf_parser.opf_parser import OPFParser
from pathvalidate import sanitize_filename

LIBRARY_PATH = '/Volumes/Scratch/calibre-staging-library-test-2'
MIRROR_PATH = '/Volumes/Scratch/test-mirror'
EXT_LIB_NAME = 'test-ext-lib'
DRY_RUN = True
SOURCE_FORMAT = '.kepub'
DEST_FORMAT = '.epub'

CONFIG_PATH = './config.yaml'
#todo add source_ext and destination_ext

def main():
    config = ConfigReader(CONFIG_PATH).config
    lib_path = config.get('library_path', LIBRARY_PATH)
    calibre = CalibreLibrary(lib_path)
    dry_run = config.get('dry_run', DRY_RUN)
    source_format = config.get('source_format', SOURCE_FORMAT)
    dest_format = config.get('dest_format', DEST_FORMAT)

    for file in calibre.list_all_opf():
        file_path = Path(file)
        parser = OPFParser(file_path.read_text())
        if parser.in_ext_lib(config.get('ext_lib_name', EXT_LIB_NAME)):
            parent_dir = os.path.dirname(file)
            matched_format = None
            for book in os.listdir(parent_dir):
                if book.endswith(source_format):
                    print(f'Found {book}')
                    matched_format = book
            if matched_format is not None:
                title = parser.get_title()
                series = parser.get_series()
                source_path = os.path.join(parent_dir, matched_format)
                #todo switch this to be <title>.<format>
                parent_link = os.path.join(config.get('mirror_path', MIRROR_PATH), series if series is not None else title)
                link_path = os.path.join(parent_link, sanitize_filename(f'{title}{dest_format}'))
                os.makedirs(parent_link, exist_ok=True)
                if not dry_run:
                    if not os.path.exists(link_path):
                        print(f'Linking {source_path} to {link_path}')
                        os.link(source_path, link_path)
                    else:
                        print(f'{link_path} already exists, skipping')
                else:
                    print(f'<DRYRUN>Linking {source_path} to {link_path}')


if __name__ == "__main__":
    main()
