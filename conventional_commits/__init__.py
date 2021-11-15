import logging


formatter = logging.Formatter("[" + " | ".join(("%(asctime)s", "%(levelname)s", "%(name)s")) + "]" + " %(message)s")

handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
