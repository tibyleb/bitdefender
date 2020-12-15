import sys
import os
import unittest
import importlib
import datetime
import configparser
import shutil
import platform

from selenium import webdriver as swd
from distutils.dir_util import copy_tree

import xml.etree.ElementTree as xet
import utilities.logger as ulogger

# import utilities.utils as utils
import HtmlTestRunner


def main(args):

    args.append('test_cases/bitdefender-com.xml')

    tree = xet.parse(args[1])
    root = tree.getroot()

    suite = unittest.TestSuite()
    # shop = root.attrib['shop']
    # version = args[2]

    # config = configparser.ConfigParser()
    # config['DEFAULT'] = {
    #     'shop' : shop,
    #     'version' : version
    # }
    # with open('run.ini', 'w') as configfile:
    #     config.write(configfile)

    logger = ulogger.Logger()
    logger.set_up()
    log = logger.get_logger()
    log.info('\n==============================================================')
    log.info('Starting test suite')

    log.info(f'Starting tests on www.bitdefender.com using test case: {str(args[1])}')

    # log.info('Testing on shop ' + shop + ' version: ' + version)
    for child in list(root):
        if child.tag == 'test-module':
            module = child.attrib['name']
            # test_type = child.attrib['type']
            class_name = module
            module = __import__('test_modules.' + module, fromlist=[class_name])
            for node in list(child):
                if node.tag == 'test-case':
                    function = node.attrib['function']
                    class_pointer = getattr(module, class_name)

                    if 'runs' in node.attrib:
                        test_runs = node.attrib['runs']
                        # log.warning('Detected multiple testruns for one Test Case - switching to DEV Mode')
                        # args[3] == 'dev'
                        for _ in range(0, int(test_runs)):
                            suite.addTest(class_pointer(function))
                    else:
                        suite.addTest(class_pointer(function))

    # # runner = unittest.TextTestRunner(verbosity=2)
    # runner = HtmlTestRunner.HTMLTestRunner(combine_reports=True, report_name='TestResults', report_title=f'Test Report - {version} : {shop}')
    # result = runner.run(suite)
    #
    # report_output = f'{runner.report_name}_{runner.timestamp}.html'
    # log.info(f'Output generated: {report_output}')
    #
    # reports_output = '/var/www/pyta/app/static/dashboard/reports'
    # ss_output = '/var/www/pyta/app/static/dashboard/screenshots/'
    # if platform.system() == 'Linux':
    #     if not os.path.isdir(reports_output):
    #         log.error(f'Reports output folder does not exist for PyTA-UI - Cannot copy reports to destination')
    #     else:
    #         shutil.copy(f'reports/{report_output}', reports_output)
    #         log.info(f'PyTA-UI report: http://pyta-ui.ovh.windeln-it.de/reports/report={report_output}')
    #
    #     if not os.path.isdir(ss_output):
    #         log.error(f'Screenshots output folder does not exist for PyTA-UI - Cannot copy reports to destination')
    #     else:
    #         copy_tree(f'screenshots/', ss_output)
    #         #log.info(f'PyTA-UI report: http://pyta-ui.ovh.windeln-it.de/reports/report={report_output}')
    #
    # test_results = {}
    #
    # for res in result.successes:
    #     log.info(f'Test: {res.test_id.split(".")[-1]} - PASS')
    #     test_results[res.test_id.split('.')[-1]] = 1
    #
    # for res in result.failures:
    #     log.error(f'Test: {res.test_id.split(".")[-1]} - FAIL')
    #     test_results[res.test_id.split('.')[-1]] = 5
    #
    # for res in result.errors:
    #     log.error(f'Test: {res.test_id.split(".")[-1]} - ERROR')
    #     test_results[res.test_id.split('.')[-1]] = 9

    # if(args[3] != 'dev'):
    #     log.info(f'Pushing test results to TestRail')
    #     utils.report_TestRail(test_results, report_output)
    #
    # os.remove('run.ini')


if __name__ == '__main__':
    main(sys.argv)
