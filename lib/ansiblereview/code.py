from fabric.api import local


def code_passes_flake8(codefile, options):
    return local("flake8 %s" % codefile, capture=True)
