"""Print Rosario's cinemas shows information"""

from datetime import date

import click

from commands.elcairo import elcairo


@click.group()
@click.option(
    "--images", help="Show images.", type=bool, default=True, show_default=True
)
@click.pass_context
def cinecli(ctx, images):
    """
    Command line interface for Rosario's cinemas shows information.
    """
    ctx.obj["images"] = images


cinecli.add_command(elcairo)

if __name__ == "__main__":
    # Each cinema will have a different way to get the information I think.
    # I cannot assume some sort of protocol, so each cinema will have a class
    # to gather the information
    cinecli(obj={})
