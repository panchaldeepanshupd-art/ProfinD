"""
ProfinD — Flask Routes & Integration Test Suite
Tests Section 12 Requirements:
- Existing product search
- Non-existent product search
- Empty search input
- Product details with valid/invalid IDs
- Deal links and safe outbound redirects
- Unauthorized access prevention
- Full admin authentication cycle
- Custom 404 error page handling
"""

import unittest
from app import app
import database


class TestProfinDRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        database.init_db()

    def setUp(self):
        self.client = app.test_client()

    def test_home_route(self):
        """Verify homepage loads with HTTP 200 and search components."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ProfinD', response.data)
        self.assertIn(b'Find the Best Price', response.data)

    def test_search_existing_product(self):
        """Verify searching for an existing product returns matching cards."""
        response = self.client.get('/products?q=iPhone')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Apple iPhone 15', response.data)
        self.assertIn(b'Compare', response.data)

    def test_search_nonexistent_product(self):
        """Verify searching for a non-existent item renders the empty-state screen."""
        response = self.client.get('/products?q=NonExistentGadget999')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No matching products found', response.data)

    def test_empty_search_validation(self):
        """Verify submitting an empty search query triggers feedback."""
        response = self.client.get('/products?q=', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a product name', response.data)

    def test_product_details_valid_id(self):
        """Verify product details page renders specs, comparison table, and DAA metrics."""
        response = self.client.get('/product/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Apple iPhone 15', response.data)
        self.assertIn(b'Store Offers Comparison', response.data)
        self.assertIn(b'DAA Algorithmic Guarantee', response.data)

    def test_product_details_invalid_id(self):
        """Verify non-existent product ID safely redirects to products catalog."""
        response = self.client.get('/product/99999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'was not found', response.data)

    def test_deal_redirect_valid(self):
        """Verify valid deal URL issues HTTP 302 redirect."""
        response = self.client.get('/deal/1')
        self.assertEqual(response.status_code, 302)
        self.assertIn('amazon.in', response.headers['Location'])

    def test_deal_redirect_invalid(self):
        """Verify non-existent deal ID gracefully redirects to products."""
        response = self.client.get('/deal/99999', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'no longer available', response.data)

    def test_unauthorized_admin_access(self):
        """Verify unauthenticated access to admin dashboard is blocked."""
        response = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login', response.headers['Location'])

    def test_admin_auth_and_dashboard_lifecycle(self):
        """Verify admin login with valid credentials and logout."""
        # Step 1: Login with valid credentials
        login_res = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'Admin@ProfinD2026'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Catalog &amp; Offer Administration', login_res.data)

        # Step 2: Access dashboard with active session
        dash_res = self.client.get('/admin/dashboard')
        self.assertEqual(dash_res.status_code, 200)

        # Step 3: Logout
        logout_res = self.client.get('/admin/logout', follow_redirects=True)
        self.assertEqual(logout_res.status_code, 200)
        self.assertIn(b'logged out', logout_res.data)

    def test_custom_404_page(self):
        """Verify unknown paths return HTTP 404 with custom styled error template."""
        response = self.client.get('/this-path-does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)


if __name__ == '__main__':
    unittest.main()
