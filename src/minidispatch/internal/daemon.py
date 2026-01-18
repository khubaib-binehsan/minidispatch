# intended to be run as a script only
# internal script to start the daemon
import time


def main() -> None:
    print("Hello World")
    time.sleep(10)
    raise ValueError("An error occurred in the daemon internal script")


if __name__ == "__main__":
    main()
