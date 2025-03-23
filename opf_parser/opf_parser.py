import xml.etree.ElementTree as ET

class OPFParser:

    def __init__(self):
        pass

    def in_ext_lib(self, lib_name, contents) -> bool:
        block = self.get_ext_lib_block(contents)
        return self.is_lib_in_block(block, lib_name)

    def get_ext_lib_block(self, contents):
        return self.extract_meta_field(contents, 'calibre:user_metadata:#ext_library')

    def is_lib_in_block(self, block, lib_name):
        return False

    @classmethod
    def extract_meta_field(cls, xml_string, field_name):
        if not xml_string:
            return None
        root = ET.fromstring(xml_string)
        for meta in root.findall("meta"):
            if meta.get("name") == field_name:
                return meta.get("content")
        return None