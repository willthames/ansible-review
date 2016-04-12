from ansiblelint import default_rulesdir, RulesCollection
from ansiblelint.formatters import ParseableFormatter
import utils
from functools import partial
import re
import os


class AnsibleReviewFormatter(object):

    def format(self, match):
        formatstr = u"{0}:{1}: [{2}] {3} {4}"
        return formatstr.format(match.filename,
                                match.linenumber,
                                match.rule.id,
                                match.message,
                                match.line
                                )


class Standard(object):
    def __init__(self, standard_dict):
        self.name = standard_dict.get("name")
        self.version = standard_dict.get("version")
        self.check = standard_dict.get("check")
        self.types = standard_dict.get("types")

    def __repr__(self):
        return "Standard: %s (version: %s, types: %s)" % (
                self.name, self.version, self.types)


class Result(object):
    def __init__(self):
        self.failed = False
        self.stderr = ""
        self.stdout = ""


class Candidate(object):
    def __init__(self, filename):
        self.path = filename
        self.version = find_version(filename)
        self.type = type(self).__name__

    def review(self, settings):
        return utils.review(self, settings)

    def __repr__(self):
        return "%s (%s)" % (type(self).__name__, self.path)

    def __getitem__(self, item):
        return self.__dict__.get(item)


class RoleFile(Candidate):
    def __init__(self, filename):
        self.path = filename
        self.version = None
        cwd = os.path.dirname(filename)
        for roleroot in [os.path.dirname(cwd), os.path.dirname(os.path.dirname(cwd))]:
            meta_file = os.path.join(roleroot, "meta", "main.yml")
            if os.path.exists(meta_file):
                self.version = self.version or find_version(meta_file)


class Playbook(Candidate):
    pass


class Task(RoleFile):
    pass


class Vars(RoleFile):
    pass


class Meta(RoleFile):
    pass


class Inventory(Candidate):
    pass


class Code(Candidate):
    pass


class Template(Candidate):
    pass


class Doc(Candidate):
    pass


class File(Candidate):
    pass


def classify(filename):
    parentdir = os.path.basename(os.path.dirname(filename))
    if parentdir in ['tasks', 'handlers']:
        return Task(filename)
    if parentdir in ['vars', 'defaults', 'group_vars', 'host_vars']:
        return Vars(filename)
    if parentdir == 'meta':
        return Meta(filename)
    if parentdir in ['inventory']:
        return Inventory(filename)
    if parentdir in ['library', 'lookup_plugins', 'callback_plugins', 
            'filter_plugins'] or filename.endswith('.py'):
        return Code(filename)
    if filename.endswith('.yml') or filename.endswith('.yaml'):
        if 'rolesfile' in filename:
            return None
        return Playbook(filename)
    if parentdir in ['templates']:
        return Template(filename)
    if parentdir in ['files']:
        return File(filename)
    if 'README' in filename:
        return Doc(filename)
    return None


def lintcheck(rulename):
    return partial(ansiblelint, rulename)


def ansiblelint(rulename, candidate, settings):
    result = Result()
    rules = RulesCollection()
    formatter = ParseableFormatter()
    rules.extend(RulesCollection.create_from_directory(default_rulesdir))
    if settings.lintdir:
        rules.extend(RulesCollection.create_from_directory(settings.lintdir))

    fileinfo = dict(path=candidate.path, type=type(candidate).__name__.lower())
    matches = rules.run(fileinfo, rulename.split(','))
    if matches:
        result.failed = True
        result.stderr = "\n".join([formatter.format(match) for match in matches])

    return result


def find_version(filename, version_regex="^# Standards: \([0-9]+(\.[0-9])+\)"):
    version_re = re.compile(version_regex)
    with open(filename, 'r') as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(0)
    return None
