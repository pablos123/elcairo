"""Print Rosario's cinemas shows information"""
import click

from commands.elcairo import elcairo


@click.group()
@click.option("--show_images", help="Show images.", is_flag=True)
@click.pass_context
def cinecli(ctx, show_images):
    """
    Command line interface for Rosario's cinemas shows information.
    """
    ctx.obj["show_images"] = show_images


cinecli.add_command(elcairo)

if __name__ == "__main__":
    # Each cinema will have a different way to get the information I think.
    # I cannot assume some sort of protocol, so each cinema will have a class
    # to gather the information
    cinecli(obj={})
