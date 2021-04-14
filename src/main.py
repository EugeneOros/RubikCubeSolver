import sys
import kociemba
from video.capture import webcam
from src.video.helpers import ColorBlock
from src.constants import E_INCORRECTLY_SCANNED, E_ALREADY_SOLVED, E_STOP


def error(state):
    if state == E_INCORRECTLY_SCANNED:
        print(ColorBlock.WARNING + '[error] Oops, you did not scan in all 6 sides correctly\nPlease try again.\n' + ColorBlock.END)
        print('Please try again.\033[0m')
    elif state == E_ALREADY_SOLVED:
        print('\033[0;33m[error] Cube has already been solved')
    elif state == E_STOP:
        print('\033[0;33m[error] Program stopped')
    sys.exit(state)


def run():
    try:
        state = webcam.run()
    except KeyboardInterrupt:
        state = E_STOP

    if isinstance(state, int) and state > 0:
        error(state)

    algorithm = kociemba.solve(state)
    length = len(algorithm.split(' '))
    print('Starting position： \n\tfront: green \n\ttop: white\n')
    print('moves: {}'.format(length))
    print('solution: {}'.format(algorithm))


if __name__ == '__main__':
    run()
