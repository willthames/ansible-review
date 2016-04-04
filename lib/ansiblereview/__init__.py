from functool import partial


class Standard(object):
    def __init__(self, standard_dict):
        self.name = standard_dict.get(name)
        self.version = standard_dict.get(version)
        self.check = standard_dict.get(check)
        self.types = standard_dict.get(types)


class Result(object):
    pass


class Success(Result):
    def __init__(self):
        self.failed = False
        self.stderr = ""


def lintcheck(rulename, rulesdir=""):
    return partial(ansiblelint(rulename=rulename, rulesdir=rulesdir))


def ansiblelint(rulename, filename, rulesdir):
    return fab.local("ansible-lint -r %s -R -t %s %s" %
            (rulesdir, rulename, filename))
