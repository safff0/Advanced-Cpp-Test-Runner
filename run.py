import argparse
from os import system as sys, chdir
from json import load

CPP_HSE_DIR = '/Users/tim/HSE/AdvancedCPP/cpp-advanced-hse'  # Absolute path
CRASHME_INPUT = 'folder/prepared_input.txt'  # Abs/Rel path to input.txt
CRASHME_SERVER = 'server.net 0000'  # format: '<address> PORT'


parser = argparse.ArgumentParser(
                    prog='compile-and-run tool for easier testing and submitting',
                    description='performs commands copied from cpp-advanced-hse/README.md',
                    epilog='yipee')

parser.add_argument('command', choices=['test', 'submit', 'crashme', 'build', 'run-scorer'])
parser.add_argument('task')
parser.add_argument('--debug', action='store_true', default=False)


args = parser.parse_args()

def go_to_taskdir() -> None:
    if args.task[0] == '/':
        args.task = args.task[1:]
    try:
        chdir(CPP_HSE_DIR + '/tasks/' + args.task)  # /<task dir>
    except:
        raise Exception(f'Wrong task path')

def go_to_build_dir() -> None:
    chdir('../../../asan_build')  # /cpp-advanced-hse/asan_build


def build(and_test: bool = False, run_scorer: bool = False) -> None:
    go_to_taskdir()
    test_names = [None]
    try:
        with open('.tester.json', 'r') as f:
            test_names = load(f)['tests']
    except:
        raise Exception('Could not find any tests')
    go_to_build_dir()
    sys(f'cmake -DCMAKE_BUILD_TYPE=ASAN{',RelWithDebInfo' if args.debug else ''} -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ..')
    if type(test_names) != list:
        test_names = [test_names];
    for test in test_names:
        print(f'Building ({test})...')
        if and_test:
            sys(f'make {test}')
            sys(f'./{test}')
        if run_scorer:
            bench = str(test).replace('test', 'bench')
            sys(f'make {bench}')
            sys(f'./{bench} --benchmark_out={bench}-report.json --benchmark_repetitions=10')
            go_to_taskdir()
            sys(f'python3 scorer.py ../../../asan_build/{bench}-report.json')
            go_to_build_dir()


if args.command == 'submit':
    go_to_taskdir()
    sys('python3 ../../../submit.py')
elif args.command == 'build':
    build()
elif args.command == 'test':
    build(and_test=True, run_scorer=True)
elif args.command == 'crashme':
    sys(f'{{ echo "{args.task}"; cat {CRASHME_INPUT}; }} | nc {CRASHME_SERVER}')
elif args.command == 'run-scorer':
    build(run_scorer=True)
else:
    raise Exception("Unknown command")