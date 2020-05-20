import os
import subprocess


def register(app):
    @app.cli.group()
    def redis():
        """Redis commands."""

    @redis.command('purge')
    def purge():
        try:
            app.redis.flushall()
        except Exception as e:
            app.logger.error(e)
            exit(1)
        app.logger.info('Redis DB purged')

    @app.cli.group()
    def test():
        """Tests commands."""

    @test.command('run')
    def run():
        try:
            subprocess.call('python -moment unittest .', shell=False)
        except Exception as e:
            app.logger.error(e)
            exit(1)
        app.logger.info('Running tests failed')

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    def update():
        """Update all languages."""
        if subprocess.call('pybabel extract -F babel.cfg -k _l -o messages.pot .', shell=False):
            raise RuntimeError('extract command failed')
        if subprocess.call('pybabel update -i messages.pot -d app/translations', shell=False):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command('compile')
    def compile_language():
        """Compile all languages."""
        if subprocess.call('pybabel compile -d app/translations', shell=False):
            raise RuntimeError('compile command failed')

    import click

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if subprocess.call('pybabel extract -F babel.cfg -k _l -o messages.pot .', shell=False):
            raise RuntimeError('extract command failed')
        if subprocess.call(
                'pybabel init -i messages.pot -d app/translations -l ' + lang, shell=False):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
