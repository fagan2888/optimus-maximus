#! /usr/bin/env python

from consts import MODEL_DIR_BASE, TO_RUN
from itertools import product
import argparse
import os
import subprocess


def run(run_args):
    num_factors, num_users, num_items, K, num_threads, input_dir, \
    base_name, output_dir, runner = run_args

    if not os.path.isdir(input_dir):
        print("Can't find %s" % input_dir)
        return

    user_weights_fname = os.path.join(input_dir, 'user_weights.csv')
    item_weights_fname = os.path.join(input_dir, 'item_weights.csv')

    base_name = os.path.join(output_dir, base_name)

    cmd = [
        runner, '-q', user_weights_fname, '-p', item_weights_fname, '-k',
        str(K), '-m',
        str(num_users), '-n',
        str(num_items), '-f',
        str(num_factors), '-t',
        str(num_threads), '--base-name', base_name
    ]
    print('Running ' + str(cmd))
    process = subprocess.Popen(cmd)
    process.wait()
    if process.returncode == 1:
        print(str(cmd) + ' failed')
    return process.returncode


# We don't run this in parallel, since we may need all the memory on the
# machine
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', required=True)
    parser.add_argument(
        '--top-K', help='list of comma-separated integers, e.g., 1,5,10,50')
    parser.add_argument('--icc', dest='icc', action='store_true')
    parser.add_argument('--no-icc', dest='icc', action='store_false')
    parser.set_defaults(icc=True)
    parser.add_argument('--mkl', dest='mkl', action='store_true')
    parser.add_argument('--no-mkl', dest='mkl', action='store_false')
    parser.set_defaults(mkl=True)
    args = parser.parse_args()

    TOP_K = [int(val) for val in args.top_K.split(',')] if args.top_K else [
        1, 5, 10, 50
    ]
    NUM_THREADS = [1]

    runner = '../cpp/blocked_mm/blocked_mm'

    BUILD_COMMAND = 'cd ../cpp/blocked_mm && make clean && make -j2'
    if args.icc:
        BUILD_COMMAND += ' ICC=1'
    if args.mkl:
        BUILD_COMMAND += ' MKL=1'
    BUILD_COMMAND += ' && cd -'
    subprocess.call(BUILD_COMMAND, shell=True)

    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for (model_dir, (num_factors, num_users, num_items, _, _), _) in TO_RUN:
        for K, num_threads in product(TOP_K, NUM_THREADS):
            result = run((num_factors, num_users,
                          num_items, K, num_threads, os.path.join(
                              MODEL_DIR_BASE, model_dir), model_dir.replace(
                                  '/', '-'), output_dir, runner))
            print(result)


if __name__ == '__main__':
    main()
