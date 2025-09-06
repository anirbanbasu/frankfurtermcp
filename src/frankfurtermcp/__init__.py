import logging
from environs import Env
from rich.logging import RichHandler

from frankfurtermcp.common import EnvironmentVariables


try:
    from icecream import ic

    ic.configureOutput(includeContext=True)
except ImportError:  # pragma: no cover
    # Graceful fallback if IceCream isn't installed.
    ic = lambda *a: None if not a else (a[0] if len(a) == 1 else a)  # noqa


env = Env()
env.read_env()

logging.basicConfig(
    level=env.str(
        EnvironmentVariables.LOG_LEVEL, default=EnvironmentVariables.DEFAULT__LOG_LEVEL
    ).upper(),
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=False, markup=True, show_path=False, show_time=False
        )
    ],
)
