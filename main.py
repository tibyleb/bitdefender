import sys
import unittest

import xml.etree.ElementTree as xet
import utilities.logger as ulogger

import HtmlTestRunner

def main(args):

    args.append('test_cases/bitdefender-com.xml')

    tree = xet.parse(args[1])
    root = tree.getroot()

    suite = unittest.TestSuite()

    logger = ulogger.Logger()
    logger.set_up()
    log = logger.get_logger()
    log.info('\n==============================================================')
    log.info('Starting test suite')

    log.info(f'Starting tests on www.bitdefender.com using test case: {str(args[1])}')

    for child in list(root):
        if child.tag == 'test-module':
            module = child.attrib['name']
            class_name = module
            module = __import__('test_modules.' + module, fromlist=[class_name])
            for node in list(child):
                if node.tag == 'test-case':
                    function = node.attrib['function']
                    class_pointer = getattr(module, class_name)
                    suite.addTest(class_pointer(function))

    runner = HtmlTestRunner.HTMLTestRunner(combine_reports=True, report_name='TestResults', report_title=f'Test Report')
    result = runner.run(suite)

    report_output = f'{runner.report_name}_{runner.timestamp}.html'
    log.info(f'Output generated: {report_output}')


    for res in result.successes:
        log.info(f'Test: {res.test_id.split(".")[-1]} - PASS')

    for res in result.failures:
        log.error(f'Test: {res.test_id.split(".")[-1]} - FAIL')

    for res in result.errors:
        log.error(f'Test: {res.test_id.split(".")[-1]} - ERROR')

if __name__ == '__main__':
    main(sys.argv)
