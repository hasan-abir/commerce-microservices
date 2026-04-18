from checkout_api.services import sendreciept_service
from django.test import TestCase
from checkout_api.models import Order, OrderItem
from unittest.mock import patch

class SendRecieptServiceTestCase(TestCase):
    def setUp(self):
        self.order = Order.objects.create(contact_email='test@test.com', total=2500, payment_intent_id='123')
        OrderItem.objects.create(item_id='1', title='Abstract Horizon Painting', price=5500, quantity=4, order=self.order)
        OrderItem.objects.create(item_id='2', title='Minimalist Ceramic Vase', price=3200, quantity=10, order=self.order)
        OrderItem.objects.create(item_id='3', title='Handwoven Cotton Throw',price=4500, quantity=2, order=self.order)

    @patch('checkout_api.services.sendmail_service')
    def test_return(self, mock_mail):
        sendreciept_service(self.order.pk)

        mock_mail.assert_called_once_with({'msg_content': 'Order Receipt\n-----------------\nHandwoven Cotton Throw (x2) - $4500\nMinimalist Ceramic Vase (x10) - $3200\nAbstract Horizon Painting (x4) - $5500\n-----------------\nTOTAL: $63000', 'subject': 'Order paid for', 'recipient': 'test@test.com'})