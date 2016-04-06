from functools import partial
from fabric.api import local


class Standard(object):
    def __init__(self, standard_dict):
        self.name = standard_dict.get("name")
        self.version = standard_dict.get("version")
        self.check = standard_dict.get("check")
        self.types = standard_dict.get("types")


class Result(object):
    pass


class Success(Result):
    def __init__(self):
        self.failed = False
        self.stderr = ""
        self.stdout = ""


def lintcheck(rulename):
    return partial(ansiblelint, rulename)


def ansiblelint(rulename, filename, settings):
    return local("ansible-lint -r %s -R -t %s --ignore-roles %s" %
                 (settings.rulesdir, rulename, filename), capture=True)
