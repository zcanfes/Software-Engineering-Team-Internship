import os
import sentry_sdk
from lm_virtuoso import logger


class Config:
    env = os.environ

    if not env.get("SENTRY_DSN"):
        logger.warning("SENTRY_DSN is not set")
    else:
        sentry_sdk.init(env.get("SENTRY_DSN"))

    if not env.get("BOUNDARY"):
        logger.warning("BOUNDARY will be set to 65")
        BOUNDARY = 65
    else:
        BOUNDARY = env.get("BOUNDARY")

    if not env.get("DEVICE_ENV"):
        logger.warning("DEVICE_ENV will be set to None")
        DEVICE_ENV = ''
    else:
        DEVICE_ENV = env.get("DEVICE_ENV")

    if not env.get("DATA_FOLDER"):
        logger.exception("DATA_FOLDER is not set")
    else:
        DIRECTORY = env.get("DATA_FOLDER")
        if not env.get("ANALYSIS_FOLDER"):
            logger.exception("ANALYSIS_FOLDER is not set")
        else:
            ANALYSIS = open(f"{env.get('ANALYSIS_FOLDER')}/analysis.txt", 'w')

    if not env.get("INSPECT_DATA") and not env.get("INSPECT_DROPPED"):
        INSPECT_DROPPED = True
        INSPECT_DATA = True
        logger.warning("The application will run all features\n")
    elif (env.get("INSPECT_DATA") is None or env.get("INSPECT_DATA").upper() == "FALSE") \
            and env.get("INSPECT_DROPPED").upper() == "TRUE":
        INSPECT_DROPPED = True
        INSPECT_DATA = False
        logger.info("The application will inspect dropped updates\n")
    elif env.get("INSPECT_DATA").upper() == "TRUE" and \
            (env.get("INSPECT_DROPPED") is None or env.get("INSPECT_DROPPED").upper() == "FALSE"):
        INSPECT_DATA = True
        INSPECT_DROPPED = False
        logger.info("The application will inspect data\n")
    elif env.get("INSPECT_DATA").upper() == "TRUE" and env.get("INSPECT_DROPPED").upper() == "TRUE":
        INSPECT_DATA = True
        INSPECT_DROPPED = True
        logger.info("The application will run all features\n")
    else:
        logger.exception(f"Invalid combination of INSPECT_DATA and INSPECT_DROPPED\n"
                         f"INSPECT_DATA: {env.get('INSPECT_DATA')}\n"
                         f"INSPECT_DROPPED: {env.get('INSPECT_DROPPED')}"
                         f"\nThe application requires at least one of the features to be set"
                         f" and to be True")
