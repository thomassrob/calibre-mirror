import os
import tempfile
import shutil
from pathlib import Path

import fs
import pytest

from calibre_library.calibre_library import CalibreLibrary

FAKE_TEST_ROOT = '/fake/test/root'


class TestCalibreLibrary:
    """Test class for CalibreLibrary functionality."""
    
    def test_empty_library(self):
        """Test that empty library returns empty list."""
        lib = CalibreLibrary('')
        assert [] == lib.list_all_opf()
    
    def test_nonexistent_path(self):
        """Test that nonexistent path returns empty list."""
        lib = CalibreLibrary('/nonexistent/path')
        assert [] == lib.list_all_opf()
    
    def test_simple_no_opf_files(self, fs):
        """Test library with no opf files."""
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'blork.txt'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'book.epub'))
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        assert [] == lib.list_all_opf()
    
    def test_single_opf_file(self, fs):
        """Test library with single opf file."""
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        expected = ['/fake/test/root/metadata.opf']
        assert expected == lib.list_all_opf()
    
    def test_multiple_opf_files_same_directory(self, fs):
        """Test library with multiple opf files in same directory."""
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'another_metadata.opf'))
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        # Only metadata.opf should be found, not another_metadata.opf
        expected = ['/fake/test/root/metadata.opf']
        assert expected == lib.list_all_opf()
    
    def test_opf_files_in_subdirectories(self, fs):
        """Test library with opf files in subdirectories."""
        # Create nested directory structure
        subdir1 = os.path.join(FAKE_TEST_ROOT, 'book1')
        subdir2 = os.path.join(FAKE_TEST_ROOT, 'book2', 'nested')
        fs.create_dir(subdir1)
        fs.create_dir(subdir2)
        
        # Create opf files in different locations
        fs.create_file(os.path.join(subdir1, 'metadata.opf'))
        fs.create_file(os.path.join(subdir2, 'metadata.opf'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
        
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        result = lib.list_all_opf()
        expected = [
            '/fake/test/root/metadata.opf',
            '/fake/test/root/book1/metadata.opf',
            '/fake/test/root/book2/nested/metadata.opf'
        ]
        # Sort both lists for comparison since order may vary
        assert sorted(expected) == sorted(result)
    
    def test_mixed_file_types(self, fs):
        """Test library with mixed file types including opf files."""
        # Create various file types
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'book.epub'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'cover.jpg'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.txt'))
        fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf.bak'))
        
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        # Only exact 'metadata.opf' should be found
        expected = ['/fake/test/root/metadata.opf']
        assert expected == lib.list_all_opf()
    
    def test_deep_nested_structure(self, fs):
        """Test library with deeply nested directory structure."""
        # Create a deep nested structure
        deep_path = os.path.join(FAKE_TEST_ROOT, 'level1', 'level2', 'level3', 'level4')
        fs.create_dir(deep_path)
        fs.create_file(os.path.join(deep_path, 'metadata.opf'))
        
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        expected = ['/fake/test/root/level1/level2/level3/level4/metadata.opf']
        assert expected == lib.list_all_opf()
    
    def test_large_library_performance(self, fs):
        """Test performance with many files (simulating large library)."""
        # Create many directories with opf files
        for i in range(100):
            subdir = os.path.join(FAKE_TEST_ROOT, f'book_{i}')
            fs.create_dir(subdir)
            fs.create_file(os.path.join(subdir, 'metadata.opf'))
            # Add some other files too
            fs.create_file(os.path.join(subdir, f'book_{i}.epub'))
            fs.create_file(os.path.join(subdir, f'cover_{i}.jpg'))
        
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        result = lib.list_all_opf()
        
        # Should find exactly 100 opf files
        assert len(result) == 100
        # All paths should contain 'metadata.opf'
        assert all('metadata.opf' in path for path in result)
    
    def test_library_path_property(self):
        """Test that the library path is stored correctly."""
        test_path = '/test/library/path'
        lib = CalibreLibrary(test_path)
        # Access the private attribute for testing
        assert lib._path == test_path
    
    def test_unicode_paths(self, fs):
        """Test handling of unicode characters in paths."""
        unicode_dir = os.path.join(FAKE_TEST_ROOT, '📚', '作者名')
        fs.create_dir(unicode_dir)
        fs.create_file(os.path.join(unicode_dir, 'metadata.opf'))
        
        lib = CalibreLibrary(FAKE_TEST_ROOT)
        result = lib.list_all_opf()
        expected = ['/fake/test/root/📚/作者名/metadata.opf']
        assert expected == lib.list_all_opf()


class TestCalibreLibraryIntegration:
    """Integration tests using real file system."""
    
    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_real_file_system(self):
        """Test with real file system operations."""
        # Create test structure
        book1_dir = os.path.join(self.temp_dir, 'book1')
        book2_dir = os.path.join(self.temp_dir, 'book2', 'nested')
        os.makedirs(book1_dir)
        os.makedirs(book2_dir)
        
        # Create opf files
        with open(os.path.join(book1_dir, 'metadata.opf'), 'w') as f:
            f.write('test content')
        with open(os.path.join(book2_dir, 'metadata.opf'), 'w') as f:
            f.write('test content')
        
        lib = CalibreLibrary(self.temp_dir)
        result = lib.list_all_opf()
        
        expected = [
            os.path.join(book1_dir, 'metadata.opf'),
            os.path.join(book2_dir, 'metadata.opf')
        ]
        assert sorted(expected) == sorted(result)
    
    def test_empty_real_directory(self):
        """Test with empty real directory."""
        lib = CalibreLibrary(self.temp_dir)
        assert [] == lib.list_all_opf()


# Keep the original simple tests for backward compatibility
def test_empty():
    lib = CalibreLibrary('')
    assert [] == lib.list_all_opf()


def test_simple(fs):
    fs.create_file(os.path.join(FAKE_TEST_ROOT, 'blork.txt'))
    lib = CalibreLibrary(FAKE_TEST_ROOT)
    assert [] == lib.list_all_opf()


def test_one(fs):
    fs.create_file(os.path.join(FAKE_TEST_ROOT, 'metadata.opf'))
    lib = CalibreLibrary(FAKE_TEST_ROOT)
    assert ['/fake/test/root/metadata.opf'] == lib.list_all_opf()
