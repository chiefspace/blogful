import unittest, os
import multiprocessing
import time
from blog import app
from io import BytesIO
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash

from blog.database import Base, engine, session, User

class UploadTest(unittest.TestCase):
    """ SetUp """
    def setUp(self):
        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Alice", email="alice@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(2)

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
    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)

if __name__ == '__main__':
   unittest.main()