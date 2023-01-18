import configparser
from dataclasses import dataclass, fields
from typing import Optional, Tuple

DOCKERFILE = "dockerfile"

DOCKER_TAG = "docker_tag"

DOCKER_REMOTE_REPOSITORY = "docker_remote_repository"

@dataclass
class DockerConfig:
    dockerfile: str
    dockerfile_context_dir: str
    docker_tag: str
    docker_remote_repository: Optional[str]

    def to_dict(self):
        return {field.name:getattr(self, field.name) for field in fields(self)}


class StateConfig:
    _latest_version: Tuple[int, int, int] = None

    def __init__(self, latest_version: str):
        print(latest_version)
        self.latest_version = latest_version

    def increment(self):
        self._latest_version = (*self._latest_version[:-1], self._latest_version[-1]+1)

    @property
    def latest_version(self):
        return ".".join(map(str, self._latest_version))

    @latest_version.setter
    def latest_version(self, value: str):
        self._latest_version = tuple(map(int, value.split(".")))

    def to_dict(self):
        return {"version": self.latest_version}

@dataclass
class ConfigServer:
    server_address: str
    server_port: str
@dataclass
class Config:
    docker_config: DockerConfig
    state: StateConfig

    def save(self, path: str):
        config = configparser.ConfigParser()
        section = self.create_section()
        config["DTQ"] = section

        with open(path, "w") as file:
            config.write(file)

    def create_section(self):
        section = {
            DOCKERFILE: self.dockerfile,
            DOCKER_TAG: self.docker_tag,
            DOCKER_REMOTE_REPOSITORY: self.docker_remote_repository,
        }
        section = {k: v for k, v in section.items() if v != ""}
        return section

    @staticmethod
    def load(path: str):
        config = configparser.ConfigParser()
        config.read(path)
        return Config(
            dockerfile=config["DTQ"].get(DOCKERFILE, ""),
            docker_tag=config["DTQ"].get(DOCKER_TAG, ""),
            docker_remote_repository=config["DTQ"].get(DOCKER_REMOTE_REPOSITORY, ""),
        )

    def tag_version_str(self) -> str:
        return ".".join(map(str, self.docker_tag_version))

    def parse_tag_version(self, value: str) -> Tuple[int, int, int]:
        return tuple(map(int, value.split(".")))
