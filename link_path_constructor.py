import os
from opf_parser.opf_parser import OPFParser
from pathvalidate import sanitize_filename


class LinkPathConstructor:
    """Class responsible for constructing link paths for books based on their metadata."""
    
    def __init__(self, mirror_path: str, dest_format: str, naming_mode: str = "komga"):
        """
        Initialize the LinkPathConstructor.
        
        Args:
            mirror_path: Base path for the mirror directory
            dest_format: Destination file format (e.g., '.epub')
            naming_mode: Organization mode - "komga" (series/title) or "audiobookshelf" (author/series/title)
        """
        self.mirror_path = mirror_path
        self.dest_format = dest_format
        self.naming_mode = naming_mode
    
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
        
        if self.naming_mode == "audiobookshelf":
            # Audiobookshelf organization: author/series_name/series_number - book_title/series_number - book_title
            if not author:
                author = "Unknown Author"
            
            if series and (series_index or series_index == 0):
                # author/series_name/series_number - book_title/series_number - book_title
                series_dir = sanitize_filename(series)
                book_dir = sanitize_filename(f'{series_index} - {title}')
                parent_link = os.path.join(self.mirror_path, sanitize_filename(author), series_dir, book_dir)
            else:
                # author/title/title (no series)
                parent_link = os.path.join(self.mirror_path, sanitize_filename(author), sanitize_filename(title))
        else:  # komga mode (default)
            # Komga organization: series/title or title/title
            directory_name = series if series else title
            if directory_name is None:
                directory_name = "Unknown"
            parent_link = os.path.join(self.mirror_path, sanitize_filename(directory_name))
        
        # Construct the filename
        if self.naming_mode == "audiobookshelf":
            if series and (series_index or series_index == 0):
                # For audiobookshelf with series, filename is just the series_number - book_title
                link_path = os.path.join(parent_link, sanitize_filename(f'{series_index} - {title}{self.dest_format}'))
            else:
                # For audiobookshelf without series, filename is just the title
                link_path = os.path.join(parent_link, sanitize_filename(f'{title}{self.dest_format}'))
        else:  # komga mode
            if series and (series_index or series_index == 0):
                link_path = os.path.join(parent_link, sanitize_filename(f'{series_index} - {title}{self.dest_format}'))
            else:
                link_path = os.path.join(parent_link, sanitize_filename(f'{title}{self.dest_format}'))
        
        return link_path 