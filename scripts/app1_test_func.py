#!/usr/bin/env python3

import sys
import argparse
import unittest
import xmlrunner

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from junitparser import JUnitXml


class PetClinicTest(unittest.TestCase):
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
    # def test_fail(self):
    #     self.assertEqual(1, 2)

    def test_success(self):
        self.assertEqual(1, 1)

    def test_title(self):
        self.assertIn("PetClinic", self.driver.title)

    def test_welcome_page(self):
        self.driver.find_element_by_xpath('//*[@id="main-navbar"]/ul/li[2]/a').click()
        self.assertTrue("Welcome" == self.driver.find_element_by_xpath("/html/body/div/div/h2").text)

    def test_oups_page(self):
        self.driver.find_element_by_xpath('//*[@id="main-navbar"]/ul/li[5]/a').click()
        self.assertTrue("Something happened..." == self.driver.find_element_by_xpath("/html/body/div/div/h2").text)

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
        suite = unittest.TestLoader().loadTestsFromTestCase(PetClinicTest)
        xmlrunner.XMLTestRunner(output=output, failfast=False, buffer=False, warnings='ignore', verbosity=2).run(suite)

    xml = JUnitXml.fromfile(args.output)

    success_rate = int(100 - (xml.failures + xml.errors) * 100 / xml.tests if xml.tests > 0 else 100)
    print(f'Success rate {success_rate}% (total={xml.tests}, errors={xml.errors}, failures={xml.failures})')

    if success_rate < args.pass_rate:
        print(f'Failing build ({success_rate} < {args.pass_rate})')
        sys.exit(1)

    sys.exit(0)
