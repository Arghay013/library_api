"""
Management command to create test users with different roles
Usage: python manage.py create_test_users
"""
from django.core.management.base import BaseCommand
from api.models import User
from library.models import Member


class Command(BaseCommand):
    help = 'Create test users with different roles for testing permissions'

    def handle(self, *args, **options):
        # Test data
        users_data = [
            {
                'username': 'librarian_user',
                'password': 'LibrarianPass123!',
                'email': 'librarian@library.com',
                'first_name': 'John',
                'last_name': 'Librarian',
                'role': 'librarian'
            },
            {
                'username': 'member_user',
                'password': 'MemberPass123!',
                'email': 'member@library.com',
                'first_name': 'Jane',
                'last_name': 'Member',
                'role': 'member'
            },
            {
                'username': 'another_member',
                'password': 'AnotherPass123!',
                'email': 'another@library.com',
                'first_name': 'Bob',
                'last_name': 'Reader',
                'role': 'member'
            },
        ]

        created_count = 0
        for user_data in users_data:
            username = user_data.pop('username')
            password = user_data.pop('password')
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {username} already exists')
                )
                continue
            
            user = User.objects.create_user(
                username=username,
                password=password,
                **user_data
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {user.get_role_display()}: {username}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully created {created_count} test users'
            )
        )
        
        # Print credentials
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST USER CREDENTIALS:')
        self.stdout.write('='*50)
        
        for user_data in users_data:
            username = user_data.get('username')
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                self.stdout.write(
                    f"\n{user.get_role_display().upper()}: {username}"
                )
                self.stdout.write(
                    f"Email: {user.email}"
                )
