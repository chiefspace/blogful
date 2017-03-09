import unittest, os
from blog import app
from io import BytesIO, StringIO
import codecs

class TestUpload(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_upload(self):
#        res=self.client.get('/upload'

# 1 define the file name
# combine or concatentat the file name with the path
# check that the file exists if not create it
# 2 if the file path with the file name does not exist go and create that file
# 3 then pass in the path to the file
# 4 reference the file using the path

# Convert to raw bytes

        x = bytes('i love the HABS', 'utf-8')

        res = self.client.post('/upload', data=dict(file=(x, "../img1.png"),))
#            file=(b'asd;lkjf;lajsd;lfj;laskjdf', "test.png"), follow_redirects=True, content_type='application/octet-stream'))
#        assert res.status_code == 200
        print("I love Boston")
        print(res.data)
        assert 'file saved' in res.data

if __name__ == '__main__':
    unittest.main()