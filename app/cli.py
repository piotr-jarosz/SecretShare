from flask import current_app


def register(app):
    @app.cli.group
    def redis():
        """Redis data commands."""
        pass

    # @redis.command()
    # def purge():
    #     r.flushall()
