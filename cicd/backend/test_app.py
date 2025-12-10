import unittest
from app import app


class BasicTests(unittest.TestCase):

    def setUp(self):
        """Alustetaan testiklinetti käyttöön."""
        self.app = app.test_client()
        self.app.testing = True

    def test_health(self):
        """Testaa että /api/health vastaa 200 OK ja sisältää 'status' avaimen."""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'status', response.data)

    def test_clock(self):
        """Testaa että /api/time endpoint toimii."""
        response = self.app.get('/api/time')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'time', response.data)


if __name__ == "__main__":
    unittest.main()
