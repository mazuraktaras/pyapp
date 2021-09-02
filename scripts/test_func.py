#!/usr/bin/env python3

import sys
import argparse

import unittest
import xmlrunner

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from junitparser import JUnitXml


class PyAppTest(unittest.TestCase):
    driver = None

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Remote(
            command_executor=args.selenium_server_url,
            desired_capabilities=DesiredCapabilities.FIREFOX
        )

        cls.driver.set_page_load_timeout(5)
        cls.driver.maximize_window()
        cls.driver.get(args.app_target_url)

    # Test for failing testing, uncomment it if need one test will be failed
    def test_fail(self):
        self.assertEqual(1, 2)

    def test_success(self):
        self.assertEqual(1, 2)

    def test_login_page(self):
        self.driver.find_element_by_link_text('Sign Up').click()
        self.driver.find_element_by_xpath('/html/body/div/nav/div/div/a')
        test = self.driver.find_element_by_xpath('/html/body/div/nav/div/div/a').text
        print(test)
        self.assertTrue("JWT BLOG" in self.driver.find_element_by_xpath('/html/body/div/nav/div/div/a').text)

    # def test_password(self):
    #     for handle in self.driver.window_handles:
    #         self.driver.switch_to.window(handle)
    #         self.driver.find_element_by_id("password")
    #         assert self. + '/web/signup' in self.driver.current_url
    #         # assert "password" in self.driver.find_element_by_id("password")

    def test_post(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.find_element_by_link_text('Posts').click()
            self.driver.find_element_by_class_name('close')
            self.assertTrue("Your token is unauthorized! LogIn, please" in self.driver.find_element_by_xpath(
                "/html/body/div/div[1]").text)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--selenium-server-url', type=str, required=True)
    parser.add_argument('--app-target-url', type=str, required=True)
    parser.add_argument('--output', type=str, default="./report.xml")
    parser.add_argument('--pass-rate', type=int, default=100)
    args = parser.parse_args()
    print(args)

    with open(args.output, 'wb') as output:
        suite = unittest.TestLoader().loadTestsFromTestCase(PyAppTest)
        xmlrunner.XMLTestRunner(output=output, failfast=False, buffer=False, warnings=None, verbosity=2).run(suite)

    # As a way to run test
    # with open(args.output, 'wt') as output:
    #     unittest.main(testRunner=xmlrunner.XMLTestRunner(output=output), exit=False)
    #     # failfast=False, buffer=False, catchbreak=False)

    xml = JUnitXml.fromfile(args.output)

    success_rate = int(100 - (xml.failures + xml.errors) * 100 / xml.tests if xml.tests > 0 else 100)
    print(f'Success rate {success_rate}% (total={xml.tests}, errors={xml.errors}, failures={xml.failures})')
    print('Success rate >>>', success_rate)
    print('Pass rate >>>', args.pass_rate)

    if success_rate < args.pass_rate:
        print(f'Failing build ({success_rate} < {args.pass_rate})')
        sys.exit(1)

    sys.exit(0)
