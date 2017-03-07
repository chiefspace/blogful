import os, io
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from werkzeug.test import Client
from werkzeug.testapp import test_app
from werkzeug.wrappers import BaseResponse
from splinter import Browser

from io import StringIO
import unittest

from flask import Request
from werkzeug import FileStorage
from werkzeug.datastructures import MultiDict

# Configure your app to use the testing database
os.environ["CONFIG_PATH"] = "blog.config.TestingConfig"

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        """ Test setup """
        self.client = app.test_client()
        self.browser = Browser("phantomjs")
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        self.app = app

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create an example user
        self.user = User(name="Mike", email="mike@example.com",
                         password=generate_password_hash("test"))
        session.add(self.user)
        session.commit()

        self.process = multiprocessing.Process(target=app.run,
                                               kwargs={"port": 8080})
        self.process.start()
        time.sleep(2)
    
    def test_login_correct(self):
        self.browser.visit("http://127.0.0.1:8080/login")
        self.browser.fill("email", "mike@example.com")
        self.browser.fill("password", "test")
        button = self.browser.find_by_css("button[type=submit]")
        button.click()
        self.assertEqual(self.browser.url, "http://127.0.0.1:8080/login")
###

    def test_add_entry(self):

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/")
        entries = session.query(Entry).all()
        self.assertEqual(len(entries), 1)

        entry = entries[0]
        self.assertEqual(entry.title, "Test Entry")
        self.assertEqual(entry.content, "Test content")
        self.assertEqual(entry.author, self.user)

    class TestingFileStorage(FileStorage):
        """
        This is a helper for testing upload behavior in your application. You
        can manually create it, and its save method is overloaded to set `saved`
        to the name of the file it was saved to. All of these parameters are
        optional, so only bother setting the ones relevant to your application.

        This was copied from Flask-Uploads.

        :param stream: A stream. The default is an empty stream.
        :param filename: The filename uploaded from the client. The default is the
                     stream's name.
        :param name: The name of the form field it was loaded from. The default is
                 ``None``.
        :param content_type: The content type it was uploaded as. The default is
                         ``application/octet-stream``.
        :param content_length: How long it is. The default is -1.
        :param headers: Multipart headers as a `werkzeug.Headers`. The default is
                    ``None``.
        """
        def __init__(self, stream=None, filename=None, name=None,
                 content_type='application/octet-stream', content_length=-1,
                 headers=None):
            FileStorage.__init__(
                self, stream, filename, name=name,
                content_type=content_type, content_length=content_length,
                headers=None)
            self.saved = None

        def save(self, dst, buffer_size=16384):
            """
            This marks the file as saved by setting the `saved` attribute to the
            name of the file it was saved to.

            :param dst: The file to save to.
            :param buffer_size: Ignored.
            """
            if isinstance(dst, basestring):
                self.saved = dst
            else:
                self.saved = dst.name

    def runTest(self):

        # Loop over some files and the status codes that we are expecting
        for filename, status_code in \
                (('foo.png', 201), ('foo.pdf', 201), ('foo.doc', 201),
                 ('foo.py', 400), ('foo', 400)):

            # The reason why we are defining it in here and not outside
            # this method is that we are setting the filename of the
            # TestingFileStorage to be the one in the for loop. This way
            # we can ensure that the filename that we are "uploading"
            # is the same as the one being used by the application
            class TestingRequest(Request):
                """A testing request to use that will return a
                TestingFileStorage to test the uploading."""
                @property
                def files(self):
                    d = MultiDict()
                    d['file'] = TestingFileStorage(filename=filename)
                    return d

            self.app.request_class = TestingRequest
            test_client = self.app.test_client()

            rv = test_client.post(
                '/upload',
                data=dict(
                    file=(StringIO('Foo bar baz'), filename),
                ))
            self.assertEqual(rv.status_code, status_code)

    def tearDown(self):
        """ Test teardown """
        # Remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()

if __name__ == "__main__":
    unittest.main()