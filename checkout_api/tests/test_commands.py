# from django.test import TestCase
# from decimal import *
# from unittest.mock import patch
# from django.core.management import call_command
# from io import StringIO

# class CleanupCartsCommandTestCase(TestCase):
#     @patch('checkout_api.management.commands.cleanup_carts.cleanupcarts_service')
#     def test_output(self, mock_service):
#         count = 3
#         mock_service.return_value = count

#         out = StringIO()
#         call_command('cleanup_carts', stdout=out)

#         mock_service.assert_called_once()

#         self.assertIn(f'Successfully deleted "{count}" abandoned carts', out.getvalue())

# class SeedProductsCommandTestCase(TestCase):
#     @patch('checkout_api.management.commands.seed_products.seedproducts_service')
#     def test_output(self, mock_service):
#         out = StringIO()
#         call_command('seed_products', stdout=out)

#         mock_service.assert_called_once()

#         self.assertIn('Successfully created 10 example products', out.getvalue())