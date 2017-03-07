import unittest, os
from blog import app
from io import BytesIO

class TestUpload(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_upload(self):
        res = self.client.post('/upload', data=dict(
        res = self.client.post('/upload', data=dict(
        ))
        assert res.status_code == 200
        print(res.data)
        assert "file saved" in res.data

if __name__ == '__main__':
    unittest.main()