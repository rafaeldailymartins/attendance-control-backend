import logging

from app.core.db import get_session, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    init_db(next(get_session()))
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
