from calibre_library.calibre_library import CalibreLibrary

PATH = '/Volumes/Scratch/calibre-staging-library-test'

def main():
    calibre = CalibreLibrary(PATH)
    print(f'All files: {calibre.list_all_opf()}')


if __name__ == "__main__":
    main()

