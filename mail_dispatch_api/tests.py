from django.test import TestCase, Client, override_settings
from mail_dispatch_api.serializers import EmailDataSerializer
from mail_dispatch_api.services import sendmail_service
from unittest.mock import patch
from django.conf import settings

class EmailSerializerTestCase(TestCase):
    def test_instance_validation(self):
        # Null validation
        serializer = EmailDataSerializer(data={})
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 3)

        self.assertEqual(str(errors['recipient'][0]), "This field is required.")
        self.assertEqual(str(errors['subject'][0]), "This field is required.")
        self.assertEqual(str(errors['msg_content'][0]), "This field is required.")

        # Blank validation
        data = {
            "recipient": "",
            "subject": "",
            "msg_content": ""
        }

        serializer = EmailDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(len(serializer.errors), 3)
        self.assertEqual(str(errors['recipient'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['subject'][0]), "This field may not be blank.")
        self.assertEqual(str(errors['msg_content'][0]), "This field may not be blank.")

        # Text limit validation
        data["subject"] = "This is very loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong text"
        serializer = EmailDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['subject'][0]), "Ensure this field has no more than 200 characters.")

        # Email validation
        data["recipient"] = "email"

        serializer = EmailDataSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        errors = serializer.errors
        self.assertEqual(str(errors['recipient'][0]), "Enter a valid email address.")

        # Successful validation
        data = {
            "recipient": "test@test.com",
            "subject": "Bro",
            "msg_content": "Gimme fuel gimme fire"
        }
        serializer = EmailDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class DispatchAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
    @patch("mail_dispatch_api.views.sendmail_task")
    def test_post(self, mock_task):
        response = self.client.post('/')
        self.assertEqual(response.status_code, 400)

        data = {
            "recipient": "test@test.com",
            "subject": "Bro",
            "msg_content": "Gimme fuel gimme fire"
        }

        response = self.client.post('/', data=data)
        self.assertEqual(response.status_code, 200)
        mock_task.delay.assert_called_once()
        mock_task.delay.assert_called_with(data)
        self.assertEqual(response.json()['msg'], "Success! We've accepted your email request and are dispatching the message now.")

class ServiceTestCase(TestCase):
    @patch("mail_dispatch_api.services.send_mail")
    def test_sendmail_service(self, mock_send_mail):
        data = {
            "recipient": "test@test.com",
            "subject": "Bro",
            "msg_content": "Gimme fuel gimme fire"
        }

        sendmail_service(data)

        mock_send_mail.assert_called_once()
        mock_send_mail.assert_called_with(data['subject'], data['msg_content'], settings.DEFAULT_FROM_EMAIL, [data['recipient']], fail_silently=False)
