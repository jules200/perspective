"""python manage.py setup_site"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from news.models import Language, MainCategory, SubCategory, SiteSettings


DATA = {
    'en': {
        'lang':  {'name':'English',     'native_name':'English',      'flag_emoji':'🇬🇧','is_default':True, 'order':1},
        'cats':  [
            ('Rwanda',         'rwanda',         1),
            ('Africa',         'africa',         2),
            ('World',          'world',          3),
            ('Research Paper', 'research-paper', 4),
        ],
        'subs':  [
            ('Politics',       'politics',      1),
            ('Economy',        'economy',       2),
            ('Education',      'education',     3),
            ('Society',        'society',       4),
            ('Culture & Arts', 'culture-arts',  5),
            ('Science & Tech', 'science-tech',  6),
            ('Religion',       'religion',      7),
            ('Environment',    'environment',   8),
            ('Health',         'health',        9),
            ('Trends',         'trends',        10),
        ],
    },
    'rw': {
        'lang':  {'name':'Kinyarwanda',  'native_name':'Ikinyarwanda', 'flag_emoji':'🇷🇼','is_default':False,'order':2},
        'cats':  [
            ('U Rwanda',                   'u-rwanda',       1),
            ('Afurika',                    'afurika',        2),
            ('Isi',                        'isi',            3),
            ("Inyandiko z'Ubushakashatsi", 'ubushakashatsi', 4),
        ],
        'subs':  [
            ('Politiki',                  'politiki',         1),
            ('Ubukungu',                  'ubukungu',         2),
            ('Uburezi',                   'uburezi',          3),
            ('Sosiyete',                  'sosiyete',         4),
            ('Umuco & Ubugeni',           'umuco-ubugeni',    5),
            ('Ubumenyi & Ikoranabuhanga', 'ubumenyi-ikora',   6),
            ('Iyobokamana',               'iyobokamana',      7),
            ('Ibidukikije',               'ibidukikije',      8),
            ('Ubuzima',                   'ubuzima',          9),
            ('Ibigezweho',                'ibigezweho',       10),
        ],
    },
}


class Command(BaseCommand):
    help = 'Create languages, categories, sub-categories, and superuser'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '═'*52)
        self.stdout.write('  The Perspectives — setup')
        self.stdout.write('═'*52)

        for code, d in DATA.items():
            lang, lc = Language.objects.get_or_create(
                code=code, defaults=d['lang'])
            self.stdout.write(f'\n  Language: {lang}')

            for name, slug, order in d['cats']:
                obj, c = MainCategory.objects.get_or_create(
                    language=lang, slug=slug,
                    defaults={'name':name,'order':order})
                self.stdout.write(f'    {"✓" if c else "·"} Cat: {name}')

            for name, slug, order in d['subs']:
                obj, c = SubCategory.objects.get_or_create(
                    language=lang, slug=slug,
                    defaults={'name':name,'order':order})
                self.stdout.write(f'    {"✓" if c else "·"} Sub: {name}')

        if not SiteSettings.objects.exists():
            SiteSettings.objects.create()
            self.stdout.write('\n  ✓ Site settings created')

        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser('admin','admin@perspectives.rw','admin123')
            self.stdout.write('  ✓ Superuser: admin / admin123')
        else:
            self.stdout.write('  · Superuser already exists')

        self.stdout.write('\n' + '═'*52)
        self.stdout.write(self.style.SUCCESS('  ✅  Done!'))
        self.stdout.write(self.style.WARNING('  EN  →  http://127.0.0.1:8000/en/'))
        self.stdout.write(self.style.WARNING('  RW  →  http://127.0.0.1:8000/rw/'))
        self.stdout.write(self.style.WARNING('  Admin → http://127.0.0.1:8000/admin/'))
        self.stdout.write('═'*52 + '\n')
