@echo off
set option=%1

if "%option%"=="-h" goto usage
if "%option%"=="--help" goto usage

REM Support single-letter options
if "%option%"=="-s" set option=--score
if "%option%"=="-c" set option=--check
if "%option%"=="-r" set option=--reformat
if "%option%"=="-t" set option=--test
if "%option%"=="-a" set option=--all

set poetry_cmd=poetry run

if "%option%"=="--score" (
    echo Scoring code...
    call :check_maintainability_and_complexity
    goto :eof
)

if "%option%"=="--check" (
    echo Checking code...
    call :check_types_and_conventions
    goto :eof
)

if "%option%"=="--reformat" (
    echo Reformatting code...
    call :reformat
    goto :eof
)

if "%option%"=="--test" (
    echo Running all unit tests...
    call :run_tests
    goto :eof
)

if "%option%"=="--all" (
    echo Reformatting code...
    call :reformat
    echo Checking code...
    call :check_types_and_conventions
    call :check_maintainability_and_complexity
    echo Testing code...
    call :run_tests
    goto :eof
)

echo Done, I'm signing off now!
call :usage
goto :eof

:reformat
    echo isort sorting your imports (does not remove non-required ones):
    %poetry_cmd% isort .\src\
    echo reformatting your code with black:
    %poetry_cmd% black .\src\
    goto :eof

:check_types_and_conventions
    echo mypy results (type checking):
    %poetry_cmd% mypy .\\src\\ugraph\\.
    echo pylint results (are there any violated conventions):
    %poetry_cmd% pylint .\\src\\ugraph\\.
    goto :eof

:check_maintainability_and_complexity
    echo maintainability as given by radon (score as number and Rank as letter)
    %poetry_cmd% radon mi .\\src\\ugraph\\.
    echo cyclomatic complexity as given by radon (score as number and Rank as letter)
    %poetry_cmd% radon cc .\\src\\ugraph\\.
    goto :eof

:run_tests
    echo Running all unit tests...
    set PYTHONPATH=.\src
    %poetry_cmd% run python -m unittest discover -s test_ugraph "*.py"
    goto :eof

:usage
    echo.
    echo POOR MANS BUILD PIPELINE
    echo "for python>=3.10 projects where Poetry is available"
    echo your code should reside in .\src
    echo .
    echo Usage: script.cmd [OPTION]
    echo.
    echo Options:
    echo --check, -c       Check code
    echo --reformat, -r    Reformat code
    echo --score, -s       Score code
    echo --test, -t        Run tests
    echo --all, -a         Execute --reformat, --check, --score, and --test
    echo -h, --help        Display this help message
    echo.
    goto :eof
