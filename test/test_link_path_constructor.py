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

    @pytest.mark.parametrize("title, series, series_index,expected_filename", [
        ('The Great Adventure', 'Fantasy/Series with \\:*?\"<>|', None, "Fantasy/Series with \\:*?\"<>|/The Great Adventure.epub"),
        ('📚 The Great Adventure 📚', '作者名 Series', 1, "作者名 Series/1 - 📚 The Great Adventure 📚.epub"),
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

    def test_author_first_with_series(self):
        """Test author-first organization with series."""
        constructor = LinkPathConstructor(self.mirror_path, '.epub', author_first=True)
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy Series"
        mock_parser.get_series_index.return_value = 1
        mock_parser.get_author.return_value = "John Doe"
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "John Doe", "Fantasy Series", "1 - The Great Adventure.epub")
        assert link_path == expected_path

    def test_author_first_without_series(self):
        """Test author-first organization without series."""
        constructor = LinkPathConstructor(self.mirror_path, '.epub', author_first=True)
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = None
        mock_parser.get_series_index.return_value = None
        mock_parser.get_author.return_value = "John Doe"
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "John Doe", "The Great Adventure", "The Great Adventure.epub")
        assert link_path == expected_path

    def test_author_first_no_author(self):
        """Test author-first organization when no author is available."""
        constructor = LinkPathConstructor(self.mirror_path, '.epub', author_first=True)
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy Series"
        mock_parser.get_series_index.return_value = 1
        mock_parser.get_author.return_value = None
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "Unknown Author", "Fantasy Series", "1 - The Great Adventure.epub")
        assert link_path == expected_path

    def test_author_first_different_format(self):
        """Test author-first organization with different destination format."""
        constructor = LinkPathConstructor(self.mirror_path, '.mobi', author_first=True)
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = "The Great Adventure"
        mock_parser.get_series.return_value = "Fantasy Series"
        mock_parser.get_series_index.return_value = 1
        mock_parser.get_author.return_value = "John Doe"
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_path = os.path.join(self.mirror_path, "John Doe", "Fantasy Series", "1 - The Great Adventure.mobi")
        assert link_path == expected_path

    @pytest.mark.parametrize("author, series, title, expected_path", [
        ('Author/Name', 'Series/Name', 'Book Title', "Author/Name/Series/Name/Book Title.epub"),
        ('Author:Name', 'Series:Name', 'Book:Title', "Author_Name/Series_Name/Book_Title.epub"),
        ('Author*Name', 'Series*Name', 'Book*Title', "Author_Name/Series_Name/Book_Title.epub"),
    ])
    def test_author_first_special_characters(self, author, series, title, expected_path):
        """Test author-first organization with special characters in names."""
        constructor = LinkPathConstructor(self.mirror_path, '.epub', author_first=True)
        
        # Create mock parser
        mock_parser = Mock(spec=OPFParser)
        mock_parser.get_title.return_value = title
        mock_parser.get_series.return_value = series
        mock_parser.get_series_index.return_value = None
        mock_parser.get_author.return_value = author
        
        link_path = constructor.construct_link_path(mock_parser, "book.kepub")
        
        expected_full_path = os.path.join(self.mirror_path, expected_path)
        assert link_path == expected_full_path


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