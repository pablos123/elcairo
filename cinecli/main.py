"""Print Rosario's cinemas shows information"""
import click

from .commands.elcairo import elcairo
from .commands.database import database


@click.group()
@click.option("--images", help="Show images.", is_flag=True, show_default=True)
@click.option(
    "--no_extra_info", help="Don't show extra info.", is_flag=True, show_default=True
)
@click.option("--urls", help="Show urls.", is_flag=True, show_default=True)
@click.pass_context
def cinecli(ctx, images, no_extra_info, urls):
    """
    Command line interface for Rosario's cinemas shows information.
    """
    ctx.obj["images"] = images
    ctx.obj["no_extra_info"] = no_extra_info
    ctx.obj["urls"] = urls


cinecli.add_command(elcairo)
cinecli.add_command(database)

def main():
    """
    Execute cinecli
    """
    cinecli(obj={})
