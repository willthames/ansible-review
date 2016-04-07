from functools import partial
from fabric.api import local
import re
import os


class Standard(object):
    def __init__(self, standard_dict):
        self.name = standard_dict.get("name")
        self.version = standard_dict.get("version")
        self.check = standard_dict.get("check")
        self.types = standard_dict.get("types")


class Result(object):
    def __init__(self):
        self.failed = False
        self.stderr = ""
        self.stdout = ""


class Playbook(object):
    def __init__(self, playbookfile):
        self.path = playbookfile
        self.version = find_version(playbookfile)


class Role(object):
    def __init__(self, rolesdir):
        self.path = rolesdir
        self.version = find_version(
            os.path.join(rolesdir, "meta", "main.yml"))


class Inventory(object):
    def __init__(self, inventoryfile):
        self.path = inventoryfile
        self.find_version = None


def lintcheck(rulename):
    return partial(ansiblelint, rulename)


def ansiblelint(rulename, filename, settings):
    lintrules = ""
    norecurse = "--ignore-roles "
    if settings.lintdir:
        lintrules = "-r %s -R " % os.path.expanduser(settings.lintdir)
    if not settings.recurse:
        norecurse = ""
    return local("ansible-lint %s -t %s %s %s" %
                 (lintrules, rulename, norecurse, filename), capture=True)


def find_version(filename, version_regex="^# Standards: \([0-9]+(\.[0-9])+\)"):
    version_re = re.compile(version_regex)
    with open(filename, 'r') as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(0)
    return None
