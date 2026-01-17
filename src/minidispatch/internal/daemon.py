# intended to be run as a script only
# internal script to start the daemon


def main() -> None:
    print("Hello World")
    raise ValueError("An error occurred in the daemon internal script")


if __name__ == "__main__":
    main()
