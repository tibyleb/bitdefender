import os
import xml.etree.ElementTree as xet
import utilities.logger as logger

log = logger.Logger()


def get_value(element):
    path = 'config/xpaths.xml'
    if not os.path.isfile(path):
        log.error(f'{path} does not exit')
        return None
    else:
        tree = xet.parse(path)
        xml_element = tree.find("element[@name='" + element + "']")
        return xml_element.attrib['value']