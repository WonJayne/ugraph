#!/usr/bin/env bash

set -e

usage() {
    echo
    echo "POOR MANS BUILD PIPELINE"
    echo "for python>=3.10 projects where Poetry is available"
    echo "your code should reside in ./src"
    echo
    echo "Usage: devtools.sh [OPTION]"
    echo
    echo "Options:"
    echo "  --check, -c       Check code"
    echo "  --reformat, -r    Reformat code"
    echo "  --score, -s       Score code"
    echo "  --test, -t        Run tests"
    echo "  --all, -a         Execute --reformat, --check, --score, and --test"
    echo "  -h, --help        Display this help message"
    echo
}

reformat() {
    echo "isort sorting your imports (does not remove non-required ones):"
    poetry run isort ./src/
    echo "reformatting your code with black:"
    poetry run black ./src/
}

check_types_and_conventions() {
    echo "mypy results (type checking):"
    poetry run mypy ./src/ugraph/.
    echo "pylint results (are there any violated conventions):"
    poetry run pylint ./src/ugraph/.
}

check_maintainability_and_complexity() {
    echo "maintainability as given by radon (score as number and Rank as letter)"
    poetry run radon mi ./src/ugraph/.
    echo "cyclomatic complexity as given by radon (score as number and Rank as letter)"
    poetry run radon cc ./src/ugraph/.
}

run_tests() {
    echo "Running all unit tests..."
    PYTHONPATH=./src poetry run python -m unittest discover -s test_ugraph
}

option="$1"

case "$option" in
    -h|--help)
        usage
        ;;
    -s|--score)
        echo "Scoring code..."
        check_maintainability_and_complexity
        ;;
    -c|--check)
        echo "Checking code..."
        check_types_and_conventions
        ;;
    -r|--reformat)
        echo "Reformatting code..."
        reformat
        ;;
    -t|--test)
        echo "Running all unit tests..."
        run_tests
        ;;
    -a|--all)
        echo "Reformatting code..."
        reformat
        echo "Checking code..."
        check_types_and_conventions
        check_maintainability_and_complexity
        echo "Testing code..."
        run_tests
        ;;
    "")
        echo "Done, I'm signing off now!"
        usage
        ;;
    *)
        echo "Unknown option: $option" >&2
        usage
        exit 1
        ;;
esac

