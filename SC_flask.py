from app import create_app, r, cli
from app.models import Secret

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'db': r, 'Secret': Secret}