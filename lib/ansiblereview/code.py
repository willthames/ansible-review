from fabric.api import local
from ansiblereview import Error, Result


def code_passes_flake8(candidate, options):
    result = local("flake8 %s" % candidate.path, capture=True)
    errors = []
    if result.failed:
        for line in result.stdout.split('\n'):
            lineno = line.split(':')[1]
            errors.append(Error(lineno, line))
    return Result(candidate.path, errors)
