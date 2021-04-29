import sys
import kociemba
from video.capture import webcam
from constants import Errors, ColorBlock


def error(state):
    if state == Errors.INCORRECTLY_SCANNED:
        print(ColorBlock.WARNING + '[error] Oops, you did not scan in all 6 sides correctly\nPlease try again.\n' + ColorBlock.END)
        print('Please try again.\033[0m')
    elif state == Errors.ALREADY_SOLVED:
        print('\033[0;33m[error] Cube has already been solved')
    elif state == Errors.STOP:
        print('\033[0;33m[error] Program stopped')
    elif state == Errors.INCORRECTLY_SCRAMBLED:
        print('\033[0;33m[error] The scanned cube does not match with generated scramble (to toggle scramble mode press \"s\"). \n Make sure you scanned the cube correctly')
    sys.exit(state)


def run():
    try:
        state = webcam.run()
    except KeyboardInterrupt:
        state = Errors.STOP

    if isinstance(state, int) and state > 0:
        error(state)

    try:
        algorithm = kociemba.solve(state)
        length = len(algorithm.split(' '))
        print('Starting position： \n\tfront: green \n\ttop: white\n')
        print('moves: {}'.format(length))
        print('solution: {}'.format(algorithm))
    except ValueError:
        error(Errors.INCORRECTLY_SCANNED)


if __name__ == '__main__':
    run()
