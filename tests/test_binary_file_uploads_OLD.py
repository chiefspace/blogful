import unittest, os, imp
from blog import app
from io import StringIO

class RestTestCase(unittest.TestCase):
    def setUp(self):
        self.dir = os.path.dirname(__file__)
        rest = imp.load_source('rest', self.dir + '/../views.py')
        rest.app.config['TESTING'] = True
        self.app = rest.app.test_client()

    def runTest(self):
        with open(self.dir + '/home/ubuntu/workspace/blog/img1.jpg', 'rb') as img1:
            img1StringIO = StringIO(img1.read())

        response = self.app.post('/upload',
                                 content_type='multipart/form-data',
                                 data={'photo': (img1StringIO, 'img1.jpg')},
                                 follow_redirects=True)
        img1StringIO.seek(0)
        assert response.data == img1StringIO.read()