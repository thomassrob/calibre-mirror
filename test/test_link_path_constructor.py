import os
import tempfile
from unittest.mock import Mock
from shutil import rmtree

import pytest

from opf_parser.opf_parser import OPFParser
from link_path_constructor import LinkPathConstructor


class TestLinkPathConstructor:
    """Test class for LinkPathConstructor functionality."""
    
    def setup_method(self):
        """Set up temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.mirror_path = '/test/mirror'
        self.dest_format = '.epub'
        self.constructor = LinkPathConstructor(self.mirror_path, self.dest_format)
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_constructor_initialization(self):
        """Test LinkPathConstructor initialization."""
        constructor = LinkPathConstructor('/test/mirror', '.epub')
        assert constructor.mirror_path == '/test/mirror'
        assert constructor.dest_format == '.epub'
    
    def test_book_with_series_and_index(self):
        """Test link path construction for book with series and series index."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy Series"
        mock_parser.get_series_index.return_value = 1
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Fantasy Series", "1 - The Great Adventure.epub")
        assert link_path == expected_path
    
    def test_book_with_series_no_index(self):
        """Test link path construction for book with series but no series index."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy Series"
        mock_parser.get_series_index.return_value = None
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Fantasy Series", "The Great Adventure.epub")
        assert link_path == expected_path
    
    def test_book_without_series(self):
        """Test link path construction for book without series."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "Standalone Book"
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Standalone Book", "Standalone Book.epub")
        assert link_path == expected_path
    
    def test_book_with_none_title(self):
        """Test link path construction when title is None."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = None
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        # expected_path = os.path.join(self.mirror_path, "Unknown", "Unknown.epub")
        assert link_path is None
    
    def test_book_with_none_series(self):
        """Test link path construction when series is None but title exists."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "Test Book"
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Test Book", "Test Book.epub")
        assert link_path == expected_path
    
    def test_book_with_special_characters_in_title(self):
        """Test link path construction with special characters in title."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "Book with /\\:*?\"<>| characters"
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        # The path should be sanitized
        expected_path = os.path.join(self.mirror_path, "Book with /\\:*?\"<>| characters", "Book with /\\:*?\"<>| characters.epub")
        # assert link_path == None
    
    def test_book_with_special_characters_in_series(self):
        """Test link path construction with special characters in series name."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy/Series with \\:*?\"<>|"
        mock_parser.get_series_index.return_value = 1
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Fantasy/Series with \\:*?\"<>|", "1 - The Great Adventure.epub")
        assert link_path == expected_path
    
    def test_different_dest_format(self):
        """Test link path construction with different destination format."""
        constructor = LinkPathConstructor(self.mirror_path, '.mobi')
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "Test Book"
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Test Book", "Test Book.mobi")
        assert link_path == expected_path
    
    def test_different_mirror_path(self):
        """Test link path construction with different mirror path."""
        constructor = LinkPathConstructor('/different/mirror/path', '.epub')
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "Test Book"
        mock_parser.get_series.return_value = "Test Series"
        mock_parser.get_series_index.return_value = 1
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join('/different/mirror/path', "Test Series", "1 - Test Book.epub")
        assert link_path == expected_path
    
    def test_unicode_characters(self):
        """Test link path construction with unicode characters."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "📚 The Great Adventure 📚"
        mock_parser.get_series.return_value = "作者名 Series"
        mock_parser.get_series_index.return_value = 1
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "作者名 Series", "1 - 📚 The Great Adventure 📚.epub")
        assert link_path == expected_path
    
    # def test_empty_strings(self):
    #     """Test link path construction with empty strings."""
    #     # Create mock parser
    #     mock_parser = Mock(spec=OPFParser)
    #     mock_parser.get_title.return_value = ""
    #     mock_parser.get_series.return_value = ""
    #     mock_parser.get_series_index.return_value = None
    #
    #     link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
    #
    #     expected_path = os.path.join(self.mirror_path, "", ".epub")
    #     assert link_path == expected_path
    #
    @pytest.mark.parametrize("title, series, series_index,expected_filename", [
        ('The Great Adventure', 'Fantasy Series', None, "Fantasy Series/The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', '', "Fantasy Series/The Great Adventure.epub"),
        ('The Great Adventure', "", 0, "The Great Adventure/The Great Adventure.epub"),
        ('The Great Adventure', None, 0, "The Great Adventure/The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 0, "Fantasy Series/0 - The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 1.5, "Fantasy Series/1.5 - The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 2.5, "Fantasy Series/2.5 - The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 0.5, "Fantasy Series/0.5 - The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 10.25, "Fantasy Series/10.25 - The Great Adventure.epub"),
        ('The Great Adventure', 'Fantasy Series', 1.0, "Fantasy Series/1.0 - The Great Adventure.epub"),
    ])
    def test_series_index_float(self, title, series, series_index, expected_filename):
        """Test link path construction with various float series indices."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = title
        mock_parser.get_series.return_value = series
        mock_parser.get_series_index.return_value = series_index
        
        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, expected_filename)
        assert link_path == expected_path

    @pytest.mark.parametrize("title, series, series_index", [
        ("", 'Fantasy Series', 0),
        (None, 'Fantasy Series', 0),
        (None, 'Fantasy Series', None),
        (None, None, 0),
        (None, None, None),
    ])
    def test_none(self, title, series, series_index):
        """Test link path construction with various float series indices."""
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = title
        mock_parser.get_series.return_value = series
        mock_parser.get_series_index.return_value = series_index

        link_path = self.constructor.construct_link_path(mock_parser, "book.kepub")

        assert link_path == None


class TestLinkPathConstructorIntegration:
    """Integration tests for LinkPathConstructor with real OPF parser."""
    
    def test_with_real_opf_parser(self):
        """Test LinkPathConstructor with a real OPFParser instance."""
        # Create a simple OPF content
        opf_content = '''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>The Test Book</dc:title>
        <dc:creator>Test Author</dc:creator>
        <meta name="calibre:series" content="Test Series"/>
        <meta name="calibre:series_index" content="1"/>
        <meta property="calibre:series_index">1</meta>
    </metadata>
</package>'''
        
        # Create temporary OPF file
        opf_path = os.path.join(tempfile.mkdtemp(), 'test.opf')
        with open(opf_path, 'w') as f:
            f.write(opf_content)
        
        try:
            # Create parser and constructor
            parser = OPFParser(opf_content)
            constructor = LinkPathConstructor('/test/mirror', '.epub')
            
            # Test link path construction
            link_path = constructor.construct_link_path(parser, "test.kepub")
            
            expected_path = os.path.join('/test/mirror', "Test Series", "1 - The Test Book.epub")
            assert link_path == expected_path
        finally:
            # Clean up
            rmtree(os.path.dirname(opf_path), ignore_errors=True)