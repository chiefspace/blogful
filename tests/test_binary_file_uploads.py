import unittest, os
from blog import app
from io import BytesIO

class UploadTest(unittest.TestCase):
    """ SetUp """
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    """ Test allowed file extension binary file upload """
    def test_upload(self):
        res1 = self.client.post('/upload', data=dict(file=(BytesIO(b"this is a test"), 'test.jpg'),), follow_redirects=True)
        assert res1.status_code == 200
        assert b'file saved' in res1.data

    """ Test disallowed file extension binary file upload """      
    def test_disallowed_file_type(self):
        res3 = self.client.post('/upload', data=dict(file=(BytesIO(b"this is a test"), 'test.txt'),), follow_redirects=True)
        assert b'file extension not allowed' in res3.data

    """ Tear Down """

if __name__ == '__main__':
   unittest.main()