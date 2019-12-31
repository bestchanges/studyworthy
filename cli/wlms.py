import click


@click.command('course')
@click.argument('subcommand')
def cli(subcommand):
    print(f'Course: {subcommand}')

