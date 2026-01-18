from __future__ import annotations

import importlib
from pathlib import Path

from minidispatch.internal.test_env import activate_test_env


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    test_home = activate_test_env(project_root)
    print(f"MINI_DISPATCH_HOME={test_home}")
    print(f"env_file={test_home / 'test_env.sh'}")

    import minidispatch.core.constants as constants

    importlib.reload(constants)

    constants.ensure_dirs()


if __name__ == "__main__":
    main()
