import unittest

from utils import xmlpost

class MyTestCase(unittest.TestCase):
    def test_something(self):
        homedir='/home/abishekg/PycharmProjects/RePlots'
        config_file = homedir+'/templates/config_postprocess.xml'
        tmpl_file = 'env_postprocess.tmpl'
        env_file = './env_postprocess.xml'
        envDict = dict()
        envDict['MACH'] ='test'
        envDict['POSTPROCESS_PATH'] = homedir+'/templates'
        envDict['CASEROOT'] = './'
        envDict['CASEROOT'] = './'
        xmlpost.create_env_file(envDict=envDict, configFile=config_file, tmplFile=tmpl_file,
                        envFile=env_file, obs_root='', comp='', standalone=True)
        #self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
