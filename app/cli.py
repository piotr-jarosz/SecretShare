def register(app):
    @app.cli.group()
    def redis():
        """Redis commands."""
        pass

    #
    @redis.command('purge')
    def purge():
        try:
            app.redis.flushall()
        except Exception as e:
            app.logger.error(e)
            exit(1)
        app.logger.info('Redis DB purged')
