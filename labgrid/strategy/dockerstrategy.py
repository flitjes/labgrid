import attr
import enum

from ..factory import target_factory
from .common import Strategy, StrategyError
from ..driver.dockerdriver import DockerDriver
from ..step import step


class Status(enum.Enum):
    """The possible states of a docker container"""
    unknown = 0
    gone = 1
    accessible = 2


@target_factory.reg_driver
@attr.s(cmp=False)
class DockerStrategy(Strategy):
    """
    DockerStrategy enables the user to directly transition to a state
    where a fresh docker container has been created and is
    ready for access (e.g. shell access via SSH if the docker image
    runs an SSH daemon).
    """
    bindings = {
        "docker_driver": DockerDriver,
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()

    @step(args=['status'])
    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == self.status:
            return  # nothing to do
        elif status == Status.accessible:
            self.target.activate(self.docker_driver)
            self.docker_driver.on()
        elif status == Status.gone:
            self.target.activate(self.docker_driver)
            self.docker_driver.off()
            self.target.deactivate(self.docker_driver)
        else:
            raise StrategyError(
                "no transition found from {} to {}".
                format(self.status, status)
            )
        self.status = status