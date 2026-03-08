import logging


def get_logger(name: str = "road_accident") -> logging.Logger:
	logger = logging.getLogger(name)
	if logger.handlers:
		return logger

	logger.setLevel(logging.INFO)
	handler = logging.StreamHandler()
	handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
	logger.addHandler(handler)
	logger.propagate = False
	return logger
