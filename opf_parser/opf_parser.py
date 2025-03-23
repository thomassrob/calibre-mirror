import json
import xml.etree.ElementTree as ET


class OPFParser:

    def __init__(self):
        pass

    def in_ext_lib(self, contents, lib_name) -> bool:
        block = self.get_ext_lib_block(contents)
        return self.is_lib_in_block(block, lib_name)

    def get_ext_lib_block(self, contents):
        return self.extract_meta_field(contents, 'calibre:user_metadata:#ext_library')

    @classmethod
    def is_lib_in_block(cls, block, lib_name):
        if block:
            json_block = json.loads(block)
            return lib_name in json_block['#value#']
        return False

    @classmethod
    def extract_meta_field(cls, xml_string, field_name):
        if not xml_string:
            return None
        try:
            root = ET.fromstring(xml_string.strip())
            for meta in root.findall(f".//*[@name='{field_name}']"):
                return meta.get("content")
        except ET.ParseError:
            return None
        return None
