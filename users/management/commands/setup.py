from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


class Command(BaseCommand):
    help = 'Thiết lập database ban đầu: migrate + seed data'

    def handle(self, *args, **options):
        self.stdout.write('1/3 Dang migrate...')
        call_command('migrate', verbosity=0)

        self.stdout.write('2/3 Dang load du lieu mau...')
        self._seed_data()

        self.stdout.write(self.style.SUCCESS('\n3/3 Hoan tat!'))
        self.stdout.write(self.style.SUCCESS('\nTai khoan mau:'))
        self.stdout.write('  Admin:        admin / 123456')
        self.stdout.write('  Bac si:       doc001-doc005 / 123456')
        self.stdout.write('  Le tan:       reception01-reception02 / 123456')
        self.stdout.write('  Benh nhan:    patient01-patient05 / 123456')

    def _seed_data(self):
        import os
        sql_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))), 'seed_data.sql')

        if not os.path.exists(sql_path):
            self.stdout.write('  -> Khong tim thay seed_data.sql, bo qua.')
            return

        self.stdout.write('  -> Dang import seed_data.sql...')
        with open(sql_path, 'r', encoding='utf-8') as f:
            raw = f.read()

        count = 0
        with connection.cursor() as cur:
            for statement in raw.split(';'):
                stmt = statement.strip()
                if stmt and not stmt.startswith('--') and not stmt.startswith('#'):
                    try:
                        cur.execute(stmt)
                        count += 1
                    except Exception as e:
                        self.stdout.write(f'  -> Bo qua: {e}')

        self.stdout.write(self.style.SUCCESS(f'  -> Da import {count} cau lenh thanh cong!'))
