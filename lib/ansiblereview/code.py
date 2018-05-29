from ansiblereview import Error, Result, utils


def code_passes_flake8(candidate, options):
    result = utils.execute(["flake8", "--max-line-length=" + str(options.maxlinelength), candidate.path])
    errors = []
    if result.rc:
        for line in result.output.strip().split('\n'):
            lineno = int(line.split(':')[1])
            errors.append(Error(lineno, line))
    return Result(candidate.path, errors)
