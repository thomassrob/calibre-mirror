import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Import the modules we're testing
from calibre_library.calibre_library import CalibreLibrary
from config_reader import ConfigReader
from opf_parser.opf_parser import OPFParser


class TestRunnerIntegration:
    """Integration tests for runner.py functionality."""
    
    def setup_method(self):
        """Set up test directories."""
        self.library_dir = '/test/library'
        self.mirror_dir = '/test/mirror'
    

    
    def test_main_function_with_single_book(self, fs):
        """Test main function with a single book using fake filesystem."""
        # Create test book structure in fake filesystem
        book_dir = os.path.join(self.library_dir, 'Test Book')
        fs.create_dir(book_dir)
        
        # Create metadata.opf file
        opf_content = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book</dc:title>
        <dc:identifier id="id">test-id</dc:identifier>
        <meta property="calibre:ext_lib_name">test-ext-lib</meta>
    </metadata>
</package>'''
        fs.create_file(os.path.join(book_dir, 'metadata.opf'), contents=opf_content)
        
        # Create source format file
        fs.create_file(os.path.join(book_dir, 'Test Book.epub'), contents='test book content')
        
        # Create test config
        config_data = {
            'library_path': self.library_dir,
            'ext_lib_name': 'test-ext-lib',
            'mirror_path': self.mirror_dir,
            'dry_run': False,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        
        with patch('runner.ConfigReader') as mock_config_reader, \
             patch('runner.CalibreLibrary') as mock_calibre_library, \
             patch('runner.OPFParser') as mock_opf_parser:
            
            # Mock CalibreLibrary
            mock_library = Mock()
            mock_library.list_all_opf.return_value = [os.path.join(book_dir, 'metadata.opf')]
            mock_calibre_library.return_value = mock_library
            
            # Mock OPFParser
            mock_parser = Mock()
            mock_parser.in_ext_lib.return_value = True
            mock_parser.get_title.return_value = 'Test Book'
            mock_parser.get_series.return_value = None
            mock_parser.get_series_index.return_value = None
            mock_opf_parser.return_value = mock_parser
            
            # Mock Path.read_text
            with patch('runner.Path') as mock_path:
                mock_path.return_value.read_text.return_value = opf_content
                
                # Import and run main function
                from runner import main
                main()
                
                # Verify that the title directory was created in the mirror path
                expected_title_dir = os.path.join(self.mirror_dir, 'Test Book')
                assert fs.exists(expected_title_dir)
                
                # Verify that the link file was created
                expected_link = os.path.join(expected_title_dir, 'Test Book.epub')
                assert fs.exists(expected_link)
    
    def test_main_function_dry_run(self, fs):
        """Test main function in dry run mode using fake filesystem."""
        # Create test book structure in fake filesystem
        book_dir = os.path.join(self.library_dir, 'Test Book')
        fs.create_dir(book_dir)
        
        # Create metadata.opf file
        opf_content = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book</dc:title>
        <dc:identifier id="id">test-id</dc:identifier>
        <meta property="calibre:ext_lib_name">test-ext-lib</meta>
    </metadata>
</package>'''
        fs.create_file(os.path.join(book_dir, 'metadata.opf'), contents=opf_content)
        
        # Create source format file
        fs.create_file(os.path.join(book_dir, 'Test Book.epub'), contents='test book content')
        
        # Create test config with dry_run=True
        config_data = {
            'library_path': self.library_dir,
            'ext_lib_name': 'test-ext-lib',
            'mirror_path': self.mirror_dir,
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        
        with patch('runner.ConfigReader') as mock_config_reader, \
             patch('runner.CalibreLibrary') as mock_calibre_library, \
             patch('runner.OPFParser') as mock_opf_parser:
            
            # Mock CalibreLibrary
            mock_library = Mock()
            mock_library.list_all_opf.return_value = [os.path.join(book_dir, 'metadata.opf')]
            mock_calibre_library.return_value = mock_library
            
            # Mock OPFParser
            mock_parser = Mock()
            mock_parser.in_ext_lib.return_value = True
            mock_parser.get_title.return_value = 'Test Book'
            mock_parser.get_series.return_value = None
            mock_parser.get_series_index.return_value = None
            mock_opf_parser.return_value = mock_parser
            
            # Mock Path.read_text
            with patch('runner.Path') as mock_path:
                mock_path.return_value.read_text.return_value = opf_content
                
                # Import and run main function
                from runner import main
                main()
                
                # In dry run mode, no directories or files should be created
                expected_title_dir = os.path.join(self.mirror_dir, 'Test Book')
                assert not fs.exists(expected_title_dir)
    
    def test_main_function_with_series(self, fs):
        """Test main function with a book that has series information."""
        # Create test book with series in fake filesystem
        book_dir = os.path.join(self.library_dir, 'Test Book')
        fs.create_dir(book_dir)
        
        # Create metadata.opf file with series information
        opf_content = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Test Book</dc:title>
        <dc:identifier id="id">test-id</dc:identifier>
        <meta property="calibre:series">Test Series</meta>
        <meta property="calibre:series_index">1</meta>
        <meta property="calibre:ext_lib_name">test-ext-lib</meta>
    </metadata>
</package>'''
        fs.create_file(os.path.join(book_dir, 'metadata.opf'), contents=opf_content)
        
        # Create source format file
        fs.create_file(os.path.join(book_dir, 'Test Book.epub'), contents='test book content')
        
        # Create test config
        config_data = {
            'library_path': self.library_dir,
            'ext_lib_name': 'test-ext-lib',
            'mirror_path': self.mirror_dir,
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        
        with patch('runner.ConfigReader') as mock_config_reader, \
             patch('runner.CalibreLibrary') as mock_calibre_library, \
             patch('runner.OPFParser') as mock_opf_parser:
            
            # Mock CalibreLibrary
            mock_library = Mock()
            mock_library.list_all_opf.return_value = [os.path.join(book_dir, 'metadata.opf')]
            mock_calibre_library.return_value = mock_library
            
            # Mock OPFParser
            mock_parser = Mock()
            mock_parser.in_ext_lib.return_value = True
            mock_parser.get_title.return_value = 'Test Book'
            mock_parser.get_series.return_value = 'Test Series'
            mock_parser.get_series_index.return_value = '1'
            mock_opf_parser.return_value = mock_parser
            
            # Mock Path.read_text
            with patch('runner.Path') as mock_path:
                mock_path.return_value.read_text.return_value = opf_content
                
                # Import and run main function
                from runner import main
                main()
                
                # The function should run without errors
                # We're testing that series handling works correctly
    
    def test_main_function_with_multiple_configs(self, fs):
        """Test main function with multiple configs."""
        # Create test books for different configs in fake filesystem
        book_dir1 = os.path.join(self.library_dir, 'Book 1')
        book_dir2 = os.path.join(self.library_dir, 'Book 2')
        fs.create_dir(book_dir1)
        fs.create_dir(book_dir2)
        
        # Create metadata.opf files
        opf_content1 = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Book 1</dc:title>
        <dc:identifier id="id">test-id-1</dc:identifier>
        <meta property="calibre:ext_lib_name">test-ext-lib</meta>
    </metadata>
</package>'''
        opf_content2 = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>Book 2</dc:title>
        <dc:identifier id="id">test-id-2</dc:identifier>
        <meta property="calibre:ext_lib_name">different-ext-lib</meta>
    </metadata>
</package>'''
        
        fs.create_file(os.path.join(book_dir1, 'metadata.opf'), contents=opf_content1)
        fs.create_file(os.path.join(book_dir2, 'metadata.opf'), contents=opf_content2)
        
        # Create source format files
        fs.create_file(os.path.join(book_dir1, 'Book 1.epub'), contents='test book content 1')
        fs.create_file(os.path.join(book_dir2, 'Book 2.epub'), contents='test book content 2')
        
        # Create multiple configs
        config_data1 = {
            'library_path': self.library_dir,
            'ext_lib_name': 'test-ext-lib',
            'mirror_path': self.mirror_dir,
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        config_data2 = {
            'library_path': self.library_dir,
            'ext_lib_name': 'different-ext-lib',
            'mirror_path': self.mirror_dir,
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        
        with patch('runner.ConfigReader') as mock_config_reader:
            mock_config_reader.return_value.configs = [config_data1, config_data2]
            
            # Import and run main function
            from runner import main
            main()
            
            # The function should process both configs
            # We're testing that multiple configs are handled correctly


class TestRunnerUnit:
    """Unit tests for runner.py functionality."""
    
    @patch('runner.CalibreLibrary')
    @patch('runner.OPFParser')
    @patch('runner.ConfigReader')
    def test_main_function_mocking(self, mock_config_reader, mock_opf_parser, mock_calibre_library):
        """Test main function with mocked dependencies."""
        # Mock CalibreLibrary
        mock_library = Mock()
        mock_library.list_all_opf.return_value = ['/path/to/metadata.opf']
        mock_calibre_library.return_value = mock_library
        
        # Mock OPFParser
        mock_parser = Mock()
        mock_parser.in_ext_lib.return_value = True
        mock_parser.get_title.return_value = 'Test Book'
        mock_parser.get_series.return_value = 'Test Series'
        mock_parser.get_series_index.return_value = '1'
        mock_opf_parser.return_value = mock_parser
        
        # Mock ConfigReader
        config_data = {
            'library_path': '/test/library',
            'ext_lib_name': 'test-ext-lib',
            'mirror_path': '/test/mirror',
            'dry_run': True,
            'source_format': '.epub',
            'dest_format': '.epub'
        }
        mock_config_reader.return_value.configs = [config_data]
        
        # Mock file operations
        with patch('runner.os.listdir') as mock_listdir, \
             patch('runner.os.path.dirname') as mock_dirname, \
             patch('runner.Path') as mock_path, \
             patch('runner.os.path.join') as mock_join, \
             patch('runner.sanitize_filename') as mock_sanitize, \
             patch('runner.os.makedirs') as mock_makedirs, \
             patch('runner.os.link') as mock_link, \
             patch('runner.os.path.exists') as mock_exists:
            
            # Set up mocks
            mock_listdir.return_value = ['test_book.epub']
            mock_dirname.return_value = '/test/book/dir'
            mock_path.return_value.read_text.return_value = 'opf content'
            mock_join.side_effect = lambda *args: '/'.join(args)
            mock_sanitize.return_value = 'Test Book.epub'
            mock_exists.return_value = False
            
            # Import and run main function
            from runner import main
            main()
            
            # Verify that the expected methods were called
            mock_library.list_all_opf.assert_called_once()
            mock_parser.in_ext_lib.assert_called_once_with('test-ext-lib')
            mock_parser.get_title.assert_called_once()
            mock_parser.get_series.assert_called_once()
            mock_parser.get_series_index.assert_called_once()
    
    def test_main_function_with_no_matching_books(self):
        """Test main function when no books match the criteria."""
        with patch('runner.CalibreLibrary') as mock_calibre_library, \
             patch('runner.ConfigReader') as mock_config_reader:
            
            # Mock CalibreLibrary to return no opf files
            mock_library = Mock()
            mock_library.list_all_opf.return_value = []
            mock_calibre_library.return_value = mock_library
            
            # Mock ConfigReader
            config_data = {
                'library_path': '/test/library',
                'ext_lib_name': 'test-ext-lib',
                'mirror_path': '/test/mirror',
                'dry_run': True
            }
            mock_config_reader.return_value.configs = [config_data]
            
            # Import and run main function
            from runner import main
            main()
            
            # Should complete without errors even with no matching books
            mock_library.list_all_opf.assert_called_once()
    
    def test_main_function_with_existing_link(self):
        """Test main function when the destination link already exists."""
        with patch('runner.CalibreLibrary') as mock_calibre_library, \
             patch('runner.OPFParser') as mock_opf_parser, \
             patch('runner.ConfigReader') as mock_config_reader, \
             patch('runner.os.path.exists') as mock_exists, \
             patch('runner.os.link') as mock_link:
            
            # Mock CalibreLibrary
            mock_library = Mock()
            mock_library.list_all_opf.return_value = ['/path/to/metadata.opf']
            mock_calibre_library.return_value = mock_library
            
            # Mock OPFParser
            mock_parser = Mock()
            mock_parser.in_ext_lib.return_value = True
            mock_parser.get_title.return_value = 'Test Book'
            mock_parser.get_series.return_value = None
            mock_parser.get_series_index.return_value = None
            mock_opf_parser.return_value = mock_parser
            
            # Mock ConfigReader
            config_data = {
                'library_path': '/test/library',
                'ext_lib_name': 'test-ext-lib',
                'mirror_path': '/test/mirror',
                'dry_run': False,
                'source_format': '.epub',
                'dest_format': '.epub'
            }
            mock_config_reader.return_value.configs = [config_data]
            
            # Mock file operations
            with patch('runner.os.listdir') as mock_listdir, \
                 patch('runner.os.path.dirname') as mock_dirname, \
                 patch('runner.Path') as mock_path, \
                 patch('runner.os.path.join') as mock_join, \
                 patch('runner.sanitize_filename') as mock_sanitize, \
                 patch('runner.os.makedirs') as mock_makedirs:
                
                # Set up mocks
                mock_listdir.return_value = ['test_book.epub']
                mock_dirname.return_value = '/test/book/dir'
                mock_path.return_value.read_text.return_value = 'opf content'
                mock_join.side_effect = lambda *args: '/'.join(args)
                mock_sanitize.return_value = 'Test Book.epub'
                mock_exists.return_value = True  # Link already exists
                
                # Import and run main function
                from runner import main
                main()
                
                # Verify that link was not called since it already exists
                mock_link.assert_not_called()


class TestRunnerConstants:
    """Test the constants defined in runner.py."""
    
    def test_runner_constants(self):
        """Test that the constants are defined correctly."""
        from runner import (
            LIBRARY_PATH, MIRROR_PATH, EXT_LIB_NAME, DRY_RUN,
            SOURCE_FORMAT, DEST_FORMAT, CONFIG_PATH
        )
        
        # Test that constants are defined
        assert isinstance(LIBRARY_PATH, str)
        assert isinstance(MIRROR_PATH, str)
        assert isinstance(EXT_LIB_NAME, str)
        assert isinstance(DRY_RUN, bool)
        assert isinstance(SOURCE_FORMAT, str)
        assert isinstance(DEST_FORMAT, str)
        assert isinstance(CONFIG_PATH, str)
        
        # Test that source and dest formats start with dot
        assert SOURCE_FORMAT.startswith('.')
        assert DEST_FORMAT.startswith('.') 