import sys

# check the system python version and require 3.5.x or greater
if not (sys.implementation.version.major==3 and sys.implementation.version.minor >=5):
    print(70 * "*")
    print("ERROR: {0} requires python >= 3.5.x. ".format(sys.argv[0]))
    print("It appears that you are running python {0}".format(
            ".".join(str(x) for x in sys.version_info[0:3])))
    print(70 * "*")
    sys.exit(1)

#
# built-in modules
#
import argparse
import collections
import errno
import getpass
import itertools
import os
import platform
from operator import itemgetter
import re
import shutil
import subprocess
import traceback

import jinja2

#
# installed dependencies
#
try:
    import lxml.etree as etree
except:
    import xml.etree.ElementTree as etree

if sys.version_info[0] == 2:
    from ConfigParser import SafeConfigParser as config_parser
else:
    from configparser import ConfigParser as config_parser


# -------------------------------------------------------------------------------
# define a class to be used for the xml entry, id, desc values
# -------------------------------------------------------------------------------
class XmlEntry(object):
    def __init__(self, id, value, desc, valid_values):
        self._id = id
        self._value = value
        self._desc = desc
        self._valid_values = valid_values

    def id(self):
        return self._id

    def value(self):
        return self._value

    def desc(self):
        return self._desc

    def valid_values(self):
        return self._valid_values


class xmlpost:
    """
    """
    def __init__(self):
        """
        """
        """
        NOTE(bja, 201605) v1 doesn't have sub-versions to worry about.
        """
        pass


    # -------------------------------------------------------------------------------
    # create_env_file - generate the XML file
    # -------------------------------------------------------------------------------
    def create_env_file(envDict, configFile, tmplFile, envFile, obs_root, comp, standalone):
        """create the XML file in the CASEROOT

        Arguments:
        envDict (dictionary) - environment dictionary
        configFile (string) - full path to input config_[definition].xml file
        tmplFile (string) - template file for output [file].xml
        envFile (string) - output [file].xml name
        obs_root (string) - observation data file root directory
        comp (string) - component
        standalone (boolean) - indicate if this is postprocessing for a standalone case

        """
        group_list = list()
        sorted_group_list = list()

        xml_tree = etree.ElementTree()
        # print ('creating configFile = {0}'.format(configFile))
        xml_tree.parse(configFile)

        for group_tag in xml_tree.findall('./groups/group'):
            xml_list = list()
            group_dict = dict()
            name = group_tag.get('name')
            order = int(group_tag.find('order').text)
            comment = group_tag.find('comment').text

            for entry_tag in group_tag.findall('entry'):
                # check if the value needs to be inherited from the envDict
                if entry_tag.get('value') == 'inherit':
                    xml_list.append(XmlEntry(entry_tag.get('id'), envDict[entry_tag.get('id')],
                                             entry_tag.get('desc'), entry_tag.get('valid_values')))
                else:
                    xml_list.append(XmlEntry(entry_tag.get('id'), entry_tag.get('value'),
                                             entry_tag.get('desc'), entry_tag.get('valid_values')))

            group_dict = {'order': order, 'name': name, 'comment': comment, 'xml_list': xml_list}
            group_list.append(group_dict)

        sorted_group_list = sorted(group_list, key=itemgetter('order'))

        # add an additional entry for machine dependent input observation files root path
        xml_list = list()
        if obs_root:
            if len(obs_root) > 0:
                xml_obs = XmlEntry('{0}DIAG_DIAGOBSROOT'.format(comp.upper()), obs_root,
                                   'Machine dependent diagnostics observation files root path', '')
                xml_list.append(xml_obs)

        # the xml_list now contains a list of XmlEntry classes that can be written to the template
        templateLoader = jinja2.FileSystemLoader(searchpath='{0}'.format(envDict['POSTPROCESS_PATH']))
        templateEnv = jinja2.Environment(loader=templateLoader)

        template = templateEnv.get_template(tmplFile)
        templateVars = {'xml_list': xml_list,
                        'group_list': sorted_group_list,
                        'standalone': standalone}

        # render the template
        env_tmpl = template.render(templateVars)

        # write the env_file
        with open(envFile, 'w') as xml:
            xml.write(env_tmpl)
