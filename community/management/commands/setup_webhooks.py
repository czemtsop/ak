from django.core.management.base import BaseCommand
from community.webhooks import WebhookEndpoint


class Command(BaseCommand):
    help = 'Setup initial webhook endpoints'

    def add_arguments(self, parser):
        parser.add_argument('--url', type=str, help='Webhook URL')
        parser.add_argument('--events', nargs='+', help='Event types to subscribe to')
        parser.add_argument('--secret', type=str, help='Webhook secret')

    def handle(self, *args, **options):
        if not options['url']:
            self.stdout.write(self.style.ERROR('URL is required'))
            return

        events = options['events'] or [
            'member.created', 'member.updated',
            'payment.created', 'loan.created',
            'announcement.created', 'event.created'
        ]

        endpoint, created = WebhookEndpoint.objects.get_or_create(
            url=options['url'],
            defaults={
                'event_types': events,
                'secret': options.get('secret', '')
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created webhook endpoint: {endpoint.url}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Webhook endpoint already exists: {endpoint.url}')
            )