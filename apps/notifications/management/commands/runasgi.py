"""
Management command to run ASGI server with enhanced configuration.
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunServerCommand


class Command(BaseCommand):
    """
    Enhanced runserver command with ASGI support.
    """
    help = 'Run ASGI development server with WebSocket support'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'addrport', nargs='?', default='127.0.0.1:8000',
            help='Optional port number, or ipaddr:port'
        )
        parser.add_argument(
            '--interface', dest='interface', default='asgi',
            choices=['wsgi', 'asgi'],
            help='Server interface to use (wsgi or asgi)'
        )
        parser.add_argument(
            '--noreload', action='store_false', dest='use_reloader',
            help='Tells Django to NOT use the auto-reloader.',
        )
        parser.add_argument(
            '--nothreading', action='store_false', dest='use_threading',
            help='Tells Django to NOT use threading.',
        )
    
    def handle(self, *args, **options):
        interface = options['interface']
        
        if interface == 'asgi':
            self.stdout.write(
                self.style.SUCCESS('Starting ASGI server with WebSocket support...')
            )
            self.run_asgi_server(options)
        else:
            self.stdout.write(
                self.style.SUCCESS('Starting WSGI server...')
            )
            self.run_wsgi_server(options)
    
    def run_asgi_server(self, options):
        """Run the ASGI development server."""
        try:
            import uvicorn
        except ImportError:
            self.stdout.write(
                self.style.ERROR(
                    'uvicorn is required for ASGI server. Install with: pip install uvicorn'
                )
            )
            return
        
        # Parse address and port
        addrport = options['addrport']
        if ':' in addrport:
            addr, port = addrport.rsplit(':', 1)
        else:
            addr, port = '127.0.0.1', addrport
        
        port = int(port)
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting ASGI server at http://{addr}:{port}/')
        )
        self.stdout.write(
            self.style.SUCCESS('WebSocket endpoint: ws://{addr}:{port}/ws/notifications/')
        )
        
        # Run uvicorn server
        uvicorn.run(
            'config.asgi:application',
            host=addr,
            port=port,
            reload=options['use_reloader'],
            log_level='info'
        )
    
    def run_wsgi_server(self, options):
        """Run the standard WSGI development server."""
        from django.core.management import execute_from_command_line
        
        # Build runserver command
        cmd = ['manage.py', 'runserver', options['addrport']]
        if not options['use_reloader']:
            cmd.append('--noreload')
        if not options['use_threading']:
            cmd.append('--nothreading')
        
        execute_from_command_line(cmd)
