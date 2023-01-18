import logging

import pytest
from docker_task_queue.client.config import DockerConfig, StateConfig

logger = logging.getLogger(__name__)


@pytest.fixture
def docker_config(faker):
    print(faker.file_name())
    return DockerConfig(
        dockerfile=faker.file_name(),
        dockerfile_context_dir=faker.file_path(),
        docker_tag=faker.name(),
        docker_remote_repository=faker.url()
    )


def test_to_dict(docker_config):
    value = docker_config.to_dict()
    excepted = {
        "dockerfile": docker_config.dockerfile,
        "dockerfile_context_dir": docker_config.dockerfile_context_dir,
        "docker_tag": docker_config.docker_tag,
        "docker_remote_repository": docker_config.docker_remote_repository
    }
    logger.debug("DockerConfig", value)
    logger.debug("Excepted", value)
    assert value == excepted

def test_constructor(faker):
    nums = tuple([faker.pyint() for _ in range(3)])
    num = ".".join(map(str, nums))
    state = StateConfig(num)
    assert state.latest_version == num
    assert state._latest_version == nums

def test_increment(faker):
    nums = tuple([faker.pyint() for _ in range(3)])
    num = ".".join(map(str, nums))
    state = StateConfig(num)
    state.increment()

    new_nums = (nums[0], nums[1], nums[2]+1)
    new_num = ".".join(map(str, new_nums))
    assert state.latest_version == new_num
    assert state._latest_version == new_nums
