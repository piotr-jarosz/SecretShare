import os


def register(app):
    @app.cli.group()
    def redis():
        """Redis commands."""
        pass

    @redis.command('purge')
    def purge():
        try:
            app.redis.flushall()
        except Exception as e:
            app.logger.error(e)
            exit(1)
        app.logger.info('Redis DB purged')

    @app.cli.group
    def test():
        """Tests commands."""
        pass

    #
    @redis.command('purge')
    def run():
        try:
            app.tests
        except Exception as e:
            app.logger.error(e)
            exit(1)
        app.logger.info('Redis DB purged')

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    def update():
        """Update all languages."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system('pybabel update -i messages.pot -d app/translations'):
            raise RuntimeError('update command failed')
        os.remove('messages.pot')

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system('pybabel compile -d app/translations'):
            raise RuntimeError('compile command failed')

    import click

    @translate.command()
    @click.argument('lang')
    def init(lang):
        """Initialize a new language."""
        if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
            raise RuntimeError('extract command failed')
        if os.system(
                'pybabel init -i messages.pot -d app/translations -l ' + lang):
            raise RuntimeError('init command failed')
        os.remove('messages.pot')
