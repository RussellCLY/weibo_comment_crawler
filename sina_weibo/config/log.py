import os

from loguru import logger

dir_path = os.path.dirname(os.getcwd()) + os.sep

logger.add('sina_weibo/log/sina_comment_{time}.log', rotation='00:00', level='INFO', encoding='utf-8')
