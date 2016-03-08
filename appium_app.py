import unittest

from appium import webdriver

import screen_storage

PLATFORM_VERSION = '4.4'


class AndroidWebViewTests(unittest.TestCase):

    def setUp(self):
        desired_caps = {
            'app': 'Browser',
            'platformName': 'Android',
            'platformVersion': PLATFORM_VERSION,
            'deviceName': 'Android Emulator'
        }

        if (PLATFORM_VERSION != '4.4'):
            desired_caps['automationName'] = 'selendroid'

        self.driver = webdriver.Remote('http://localhost:4723/wd/hub',
                                       desired_caps)

    def testDOM(self):
        self.driver.get('http://www.bing.com/')
        screen_storage.DOM(self.driver)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AndroidWebViewTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
