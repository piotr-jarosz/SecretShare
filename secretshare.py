from app import create_app, cli
from app.models import Secret

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'R': app.redis, 'Secret': Secret}