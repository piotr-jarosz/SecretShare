from app import r


def register(app):
    @app.cli.group
    def redis():
        """Redis data commands."""
        pass

    # @redis.command()
    # def purge():
    #     r.flushall()
