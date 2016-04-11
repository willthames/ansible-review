from fabric.api import local


def code_passes_flake8(candidate, options):
    return local("flake8 %s" % candidate.path, capture=True)
