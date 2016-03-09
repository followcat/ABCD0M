import time
import unittest

from appium import webdriver

import screen_storage
from images import image_diff

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
        self.driver.switch_to.context('NATIVE_APP')
        self.driver.tap([(240, 68)])
        time.sleep(0.5)
        self.driver.tap([(20, 68)])
        time.sleep(0.5)
        self.driver.tap([(240, 400)])
        time.sleep(0.5)

    def testIndexDOM(self):
        self.driver.switch_to.context('WEBVIEW_1')
        self.driver.get('http://10.0.0.105:5000/')
        self.indexDOM = screen_storage.DOM(self.driver)
        indexShot = screen_storage.webviewfullscreen(self.driver)
        indexShot.save('/tmp/im1.png')

        self.driver.switch_to.context('WEBVIEW_1')
        self.driver.get('http://10.0.0.105:5000/mod')
        self.indexModDOM = screen_storage.DOM(self.driver)
        indexModShot = screen_storage.webviewfullscreen(self.driver)
        indexModShot.save('/tmp/im2.png')

        image_diff('/tmp/im1.png', '/tmp/im2.png', '/tmp/diff.png', (0,255,0))

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AndroidWebViewTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
