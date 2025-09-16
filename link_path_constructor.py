import os
from opf_parser.opf_parser import OPFParser
from pathvalidate import sanitize_filename


class LinkPathConstructor:
    """Class responsible for constructing link paths for books based on their metadata."""
    
    def __init__(self, mirror_path: str, dest_format: str, author_first: bool = False):
        """
        Initialize the LinkPathConstructor.
        
        Args:
            mirror_path: Base path for the mirror directory
            dest_format: Destination file format (e.g., '.epub')
            author_first: If True, organize by author/series/title, otherwise series/title or title/title
        """
        self.mirror_path = mirror_path
        self.dest_format = dest_format
        self.author_first = author_first
    
    def construct_link_path(self, parser: OPFParser, matched_format: str) -> str | None:
        """
        Construct the link path for a book based on its metadata.
        
        Args:
            parser: OPFParser instance containing book metadata
            matched_format: The matched format filename
            
        Returns:
            The constructed link path for the book
        """
        if not (title := parser.get_title()):
            return None

        series = parser.get_series()
        series_index = parser.get_series_index()
        author = parser.get_author()
        
        if self.author_first:
            # Author-first organization: author/series/title or author/title/title
            if not author:
                author = "Unknown Author"
            
            if series:
                # author/series/title
                parent_link = os.path.join(self.mirror_path, sanitize_filename(author), sanitize_filename(series))
            else:
                # author/title/title
                parent_link = os.path.join(self.mirror_path, sanitize_filename(author), sanitize_filename(title))
        else:
            # Original organization: series/title or title/title
            directory_name = series if series else title
            if directory_name is None:
                directory_name = "Unknown"
            parent_link = os.path.join(self.mirror_path, sanitize_filename(directory_name))
        
        # Construct the filename
        if series and (series_index or series_index == 0):
            link_path = os.path.join(parent_link, sanitize_filename(f'{series_index} - {title}{self.dest_format}'))
        else:
            link_path = os.path.join(parent_link, sanitize_filename(f'{title}{self.dest_format}'))
        
        return link_path 