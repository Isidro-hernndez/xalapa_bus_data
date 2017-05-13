#!/usr/bin/env python3
import argparse
from functools import wraps
import os
import subprocess
from lib.stops import *
from lib.tasks import UncompressTask, ConvertTask, ExtractStopsTask, DumpStopsTask, ComputeBoundsTask

available_tasks = dict()

UncompressTask().register(available_tasks)
ConvertTask().register(available_tasks)
ExtractStopsTask().register(available_tasks)
DumpStopsTask().register(available_tasks)
ComputeBoundsTask().register(available_tasks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Apply different administrative tasks to data')

    parser.add_argument('task', choices=available_tasks, help='the task to perform')

    args = parser.parse_args()

    for parent, dirs, files in os.walk('data'):
        available_tasks[args.task].on_process(parent, dirs, files)

    available_tasks[args.task].on_finish()
