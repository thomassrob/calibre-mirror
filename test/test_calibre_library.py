import os

import fs
import pytest

from calibre_library.calibre_library import CalibreLibrary

FAKE_TEST_ROOT = '/fake/test/root'


def test_empty():
    lib = CalibreLibrary('')
    assert [] == lib.list_all_opf()


def test_simple(fs):
    fs.create_file(os.path.join(FAKE_TEST_ROOT, 'blork.txt'))
    lib = CalibreLibrary(FAKE_TEST_ROOT)
    assert [] == lib.list_all_opf()
    # fs.reset()

def test_one(fs):
    fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
    lib = CalibreLibrary(FAKE_TEST_ROOT)
    assert ['/fake/test/root/metadata.opf'] == lib.list_all_opf()
    # fs.reset()
