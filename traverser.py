from utils.argument_parser import Parser as ArgParser
from delivery_service import DeliveryService


def main() -> None:
    args = ArgParser().parse()
    DeliveryService(args=args).run()


if __name__ == "__main__":
    main()
