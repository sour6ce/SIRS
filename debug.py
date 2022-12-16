'''
    All code to debug, log and profile the project goes here.
'''
import cProfile as prof
import logging
import os
import pstats as st
from datetime import datetime
from os import path
from typing import Any, Callable, Dict, Iterable

from config import *

EXECUTION_ID = (str(datetime.now())).replace(' ', '-').replace(':', '-')


def debugExcepSilence(f: Callable):
    def __wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            logging.log(
                logging.WARNING,
                f"Debug system fail (Exception raised):\n\t{str(e)}"
            )

    return __wrapper


@debugExcepSilence
def setupRootLog():
    log_dir = path.abspath(path.join(path.dirname(__file__), 'logs'))

    log_file = path.join(
        log_dir,
        f"{EXECUTION_ID}.log"
    )

    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(filename=log_file, filemode='w',
                        level=logging.DEBUG if DEBUG else logging.WARNING)


@debugExcepSilence
def setupRootLogForTests(test_name: str):
    log_dir = path.abspath(
        path.join(path.dirname(__file__),
                  'logs', 'tests', test_name))

    log_file = path.join(
        log_dir,
        f"{EXECUTION_ID}.log"
    )

    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(filename=log_file, filemode='w',
                        level=logging.DEBUG if DEBUG else logging.WARNING)


__profiles__ = {}


@debugExcepSilence
def profileFunc(
        function: Callable, *_, f_args: Iterable[Any],
        f_kwargs: Dict[str, Any],
        limit: int = 150):
    # Only profile if DEBUG is True
    if not DEBUG:
        r = function(*f_args, **f_kwargs)
        return r

    # Profiler initialization
    prof_dir = path.abspath(path.join(path.dirname(
        __file__), 'profiles'))

    profile_count = __profiles__.get(function.__name__, 0)+1

    PROFILE_ID = f"{function.__name__}.{profile_count:03d}"

    if PROFILE_DIR is not None:
        prof_dir = path.abspath(PROFILE_DIR)

    os.makedirs(prof_dir, exist_ok=True)

    prof_filename = path.join(
        prof_dir,
        f"{EXECUTION_ID}.{PROFILE_ID}.profile"
    )

    prof_file = open(prof_filename, mode='w')

    __profiles__[function.__name__] = profile_count
    pr = prof.Profile()

    pr.enable()  # Start Profiling

    r = function(*f_args, **f_kwargs)

    pr.disable()  # End profiling

    # Write profiler stats
    st.Stats(pr, stream=prof_file).sort_stats(
        st.SortKey.CUMULATIVE).print_stats(limit)

    prof_file.close()

    return r  # Return the same the function returned


def profile(limit: int = 150):
    def __profile_wrap(f: Callable):
        # Reduce nesting if not in DEBUG
        if not DEBUG:
            return f
        
        def __wrapper(*args, **kwargs):
            profileFunc(f, f_args=args, f_kwargs=kwargs, limit=limit)

        return __wrapper

    return __profile_wrap
