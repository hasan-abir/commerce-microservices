# Commerce Microservices

## Checkout Microservice

- First, it allows adding items to cart without any authentication (session auth rather).
- After validating the request body and the items added, the API sends only the request body to the **Place Order** Service (the celery task) and stores it in a queue in redis, leaving the cart items out, as they can be accessed later from the DB.
- The Place Order Service turns the cart items into order items while simultanously creating an order, and stores static values in them, some of which (mainly the totals) goes back to the user through email. This service can handle payment systems too, depending on if the user wants to pay digitally.
- Once the order process is completed, the cart becomes empty again and the product stock number goes down by however many were ordered.

The ENV variables that are required:

```
DEFAULT_FROM_EMAIL=

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
```

And that are optional but recommended:

```
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS= true or false
EMAIL_USE_SSL= true or false
```

## Send Mail Microservice

Tells the API to send the mail to the worker. And the worker gets the job done whenever it feels like it (almost the next instance, in a queue). And so, a 100 emails sent at once won't cause the endpoint any headache whatsoever, a 100 or a 1000.

By default, this project uses Mailhog as a dummy email host, but it's easy enough to configure a real world email host instead. To do that, create a `.env` in root directory, and fill it up with email configurations.

## Run with Docker (recommended)

`docker compose up --build --watch`

Add `sudo` beforehand if permission is required

Go to `http://localhost:8000` to check the API docs and `http://localhost:8025` to check the email (if using mailhog)

## Test with Docker too

While the server is running, run `docker compose exec api python manage.py test checkout_api.tests`

## Resources used

- [Celery installation](https://docs.celeryq.dev/en/v5.5.3/getting-started/introduction.html#installation)
- [Celery configuration](https://docs.celeryq.dev/en/v5.5.3/django/first-steps-with-django.html)
- [DRF](https://www.django-rest-framework.org/) and [Django](https://docs.djangoproject.com/en/6.0/)
- [DRF spectacular](https://github.com/tfranzel/drf-spectacular)
