import logging
from subprocess import check_output

SCORER = '/usr/bin/java -jar ../bin/ss.jar -s'
LOGGER = logging.getLogger(__name__)


def evaluate_wsi(key_file, filename):
    """Agirre's single sense WSI system evaluation is used.  Details:
    http://www.aclweb.org/anthology/S07-1002"""

    score = check_output('{} {} {} | tail -2 | head -1'
                         .format(SCORER, key_file, filename), shell=True)
    _, precision, recall, f1score = score.split()
    return map(float, [precision, recall, f1score])