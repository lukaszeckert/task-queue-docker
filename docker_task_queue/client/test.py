import configparser
import time

import click
import docker
from celery import Celery

from client.config import Config

DEFAULT_CFG = ".dtq.ini"


def configure(ctx, param, filename):
    cfg = Config.load(filename)
    ctx.default_map = {
        "dockerfile": cfg.dockerfile,
        "docker_tag": cfg.docker_tag,
        "docker_remote_repository": cfg.docker_remote_repository,
    }
    return cfg


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--dockerfile", required=True, help="Dockerfile used when building project."
)
@click.option(
    "--docker_context_dir", default=".", help="Context directory for docker build"
)
@click.option(
    "--docker_tag", required=True, help="Tag used for docker images when building"
)
@click.option(
    "--docker_remote_repository",
    default="",
    help="Docker repository to where to push images. When left blank, dtq will not push images.",
)
def init(dockerfile, docker_context_dir, docker_tag, docker_remote_repository):
    """can be used to initialize constant default cli values.
    This will create .dtq.ini file inside working directory."""
    config = Config(
        dockerfile=dockerfile,
        dockerfile_context_dir=docker_context_dir,
        docker_tag=docker_tag,
        docker_remote_repository=docker_remote_repository,
        docker_tag_version=(0, 0, 0),
    )
    config.save(".dtq.ini")


@cli.command()
@click.option(
    "--dockerfile", required=False, help="Dockerfile used when building project."
)
@click.option(
    "--docker_context_dir", required=False, help="Context directory for docker build"
)
@click.option(
    "--docker_tag", required=False, help="Tag used for docker images when building"
)
@click.option(
    "--docker_remote_repository",
    default="",
    help="Docker repository to where to push images. When left blank, dtq will not push images.",
)
def update(dockerfile, docker_context_dir, docker_tag, docker_remote_repository):
    """Similar to init, but it will update existing values instead of overwriting them."""
    config = Config.load(".dtq.ini")
    if dockerfile:
        config.dockerfile = dockerfile
    if docker_tag:
        config.docker_tag = docker_tag
    if docker_remote_repository:
        config.docker_remote_repository = docker_remote_repository
    if docker_context_dir:
        config.docker_context_dir = docker_context_dir
    config.save(DEFAULT_CFG)


@cli.command()
@click.option(
    "-c",
    "--config",
    type=click.Path(dir_okay=False),
    default=DEFAULT_CFG,
    callback=configure,
    is_eager=True,
    expose_value=True,
    help="Read option defaults from the specified INI file",
    show_default=True,
)
@click.option(
    "--dockerfile", required=False, help="Dockerfile used when building project."
)
@click.option("--docker_tag", help="Tag used for docker images when building")
@click.option(
    "--docker_remote_repository",
    default="",
    help="Docker repository to where to push images. When left blank, dtq will not push images.",
)
def build(
    config,
    dockerfile,
    docker_tag,
    docker_remote_repository,
):
    client = docker.from_env()
    config.increment_version()
    version = config.tag_version_str()
    client.images.build(dockerfile=dockerfile, tag=f"{docker_tag}:{version}", path=".")


if __name__ == "__main__":
    cli(obj={})
