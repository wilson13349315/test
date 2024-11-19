import os
import logging
import datetime
import sys


def initiate_log_file():
    timestamp = datetime.date.today().strftime('%Y%m%d')
    path = rf'C:\Users\{os.getlogin()}\rystadenergy.com\rystadenergy.com - Gas\VR\BenchmarkLog'

    if not os.path.exists(path+'\\'+timestamp[:-2]):
        os.makedirs(path+'\\'+timestamp[:-2])

    filename = path+'\\'+timestamp[:-2]+'/'+timestamp+f'_{os.getlogin()}.log'

    # Check if filename exist, if true add an int as suffix
    if os.path.isfile(filename):
        expand = 1
        while True:
            expand += 1
            new_filename = filename.split(".log")[0] + '_' + str(expand) + ".log"
            if os.path.isfile(new_filename):
                continue
            else:
                filename = new_filename
                break

    return filename


def initiate_logger(run_file):
    filename = initiate_log_file()
    logging.basicConfig(filename=filename,
                        filemode='a',
                        level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(name)s - [ %(message)s ]",
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(run_file)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    logging.getLogger('numexpr').setLevel(logging.WARNING)
    logging.getLogger('pdfminer').setLevel(logging.WARNING)
    logging.getLogger('camelot').setLevel(logging.WARNING)
    logging.getLogger('WDM').setLevel(logging.WARNING)

    return logger

