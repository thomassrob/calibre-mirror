import os
from pathlib import Path

from calibre_library.calibre_library import CalibreLibrary
from config_reader import ConfigReader
from opf_parser.opf_parser import OPFParser
from pathvalidate import sanitize_filename
from link_path_constructor import LinkPathConstructor

LIBRARY_PATH = '/Volumes/Scratch/calibre-staging-library-test-2'
MIRROR_PATH = '/Volumes/Scratch/test-mirror'
EXT_LIB_NAME = 'test-ext-lib'
DRY_RUN = True
SOURCE_FORMAT = '.kepub'
DEST_FORMAT = '.epub'

CONFIG_PATH = './config.yaml'





def main():
    configs = ConfigReader(CONFIG_PATH).configs
    for config_group in configs:
        lib_path = config_group.get('library_path', LIBRARY_PATH)
        calibre = CalibreLibrary(lib_path)
        dry_run = config_group.get('dry_run', DRY_RUN)
        source_format = config_group.get('source_format', SOURCE_FORMAT)
        dest_format = config_group.get('dest_format', DEST_FORMAT)
        
        # Create LinkPathConstructor instance for this config
        link_constructor = LinkPathConstructor(
            config_group.get('mirror_path', MIRROR_PATH), 
            dest_format,
            config_group.get('author_first', False)
        )

        for file in calibre.list_all_opf():
            file_path = Path(file)
            parser = OPFParser(file_path.read_text())
            if parser.in_ext_lib(config_group.get('ext_lib_name', EXT_LIB_NAME)):
                parent_dir = os.path.dirname(file)
                matched_format = None
                for book in os.listdir(parent_dir):
                    if book.endswith(source_format):
                        print(f'Found {book}')
                        matched_format = book
                if matched_format is not None:
                    source_path = os.path.join(parent_dir, matched_format)
                    link_path = link_constructor.construct_link_path(parser, matched_format)
                    parent_link = os.path.dirname(link_path)
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
