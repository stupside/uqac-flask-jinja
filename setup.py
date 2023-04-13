from setuptools import setup, find_packages

requires = [
    # Web
    'flask',

    # Configuration
    'python-dotenv',

    # Database
    'peewee',
    'psycopg2-binary',

    # Redis
    'redis',
    'rq',

    # Serialization
    'dacite',
]

packages = find_packages()

setup(
    name='src',
    version='0.0',
    author='Kilian .H',
    author_email='khoupeurt@edu.uqac.ca',
    packages=packages,
    include_package_data=True,
    install_requires=requires
)
