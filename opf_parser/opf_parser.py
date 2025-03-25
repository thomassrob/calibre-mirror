import json
import xml.etree.ElementTree as ET


class OPFParser:

    def __init__(self, contents: str):
        self._contents = contents

    def in_ext_lib(self, lib_name) -> bool:
        block = self._get_ext_lib_block()
        return self.is_lib_in_block(block, lib_name)

    def _get_ext_lib_block(self):
        return self.extract_meta_field('calibre:user_metadata:#ext_library')

    @classmethod
    def is_lib_in_block(cls, block, lib_name):
        if block:
            json_block = json.loads(block)
            return lib_name in json_block['#value#']
        return False

    def extract_meta_field(self, field_name):
        element = self.extract_element(f".//*[@name='{field_name}']")
        return element.get("content") if element != None else None

    def extract_element(self, expression: str):
        if not self._contents:
            return None
        try:
            root = ET.fromstring(self._contents.strip())
            for meta in root.findall(expression):
                return meta
        except ET.ParseError:
            return None
        return None

    def get_title(self):
        element = self.extract_element('.//{http://purl.org/dc/elements/1.1/}title')
        return element.text if element != None else None

    def get_series(self):
        element = self.extract_meta_field('calibre:series')
        return element.text if element != None else None
