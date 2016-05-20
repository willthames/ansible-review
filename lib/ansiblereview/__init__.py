from ansiblelint import default_rulesdir, RulesCollection
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


class Error(object):
    def __init__(self, lineno, message):
        self.lineno = lineno
        self.message = message

    def __repr__(self):
        if self.lineno:
            return "%s: %s" % (self.lineno, self.message)
        else:
            return self.message


class Result(object):
    def __init__(self, candidate, errors=[]):
        self.candidate = candidate
        self.errors = errors

    def message(self):
        return "\n".join(["{0}:{1}".format(self.candidate, error)
                          for error in self.errors])


class Candidate(object):
    def __init__(self, filename):
        self.path = filename
        self.version = find_version(filename)
        self.filetype = type(self).__name__.lower()
        self.expected_version = True

    def review(self, settings, lines=None):
        return utils.review(self, settings, lines)

    def __repr__(self):
        return "%s (%s)" % (type(self).__name__, self.path)

    def __getitem__(self, item):
        return self.__dict__.get(item)


class RoleFile(Candidate):
    def __init__(self, filename):
        super(RoleFile, self).__init__(filename)
        self.version = None
        parentdir = os.path.dirname(os.path.abspath(filename))
        while parentdir != os.path.dirname(parentdir):
            meta_file = os.path.join(parentdir, "meta", "main.yml")
            if os.path.exists(meta_file):
                self.version = find_version(meta_file)
                if self.version:
                    break
            parentdir = os.path.dirname(parentdir)


class Playbook(Candidate):
    pass


class Task(RoleFile):
    def __init__(self, filename):
        super(Task, self).__init__(filename)
        self.filetype = 'tasks'


class Vars(Candidate):
    pass


class Unversioned(Candidate):
    def __init__(self, filename):
        super(Unversioned, self).__init__(filename)
        self.expected_version = False


class InventoryVars(Unversioned):
    pass


class RoleVars(RoleFile):
    pass


class Meta(RoleFile):
    pass


class Inventory(Unversioned):
    pass


class Code(Unversioned):
    pass


class Template(RoleFile):
    pass


class Doc(Unversioned):
    pass


class File(RoleFile):
    pass


class Rolesfile(Unversioned):
    pass


def classify(filename):
    parentdir = os.path.basename(os.path.dirname(filename))
    if parentdir in ['tasks', 'handlers']:
        return Task(filename)
    if parentdir in ['vars', 'defaults']:
        return RoleVars(filename)
    if parentdir in ['group_vars', 'host_vars']:
        return InventoryVars(filename)
    if parentdir == 'meta':
        return Meta(filename)
    if parentdir in ['inventory']:
        return Inventory(filename)
    if parentdir in ['library', 'lookup_plugins', 'callback_plugins',
                     'filter_plugins'] or filename.endswith('.py'):
        return Code(filename)
    if filename.endswith('.yml') or filename.endswith('.yaml'):
        if 'rolesfile' in filename:
            return Rolesfile(filename)
        return Playbook(filename)
    if 'templates' in filename.split(os.sep):
        return Template(filename)
    if 'files' in filename.split(os.sep):
        return File(filename)
    if 'README' in filename:
        return Doc(filename)
    return None


def lintcheck(rulename):
    return partial(ansiblelint, rulename)


def ansiblelint(rulename, candidate, settings):
    result = Result(candidate.path)
    rules = RulesCollection()
    rules.extend(RulesCollection.create_from_directory(default_rulesdir))
    if settings.lintdir:
        rules.extend(RulesCollection.create_from_directory(settings.lintdir))

    fileinfo = dict(path=candidate.path, type=candidate.filetype)
    matches = rules.run(fileinfo, rulename.split(','))
    result.errors = [Error(match.linenumber, "[%s] %s" % (match.rule.id, match.message))
                     for match in matches]
    return result


def find_version(filename, version_regex="^# Standards: ([0-9]+\.[0-9]+)"):
    version_re = re.compile(version_regex)
    with open(filename, 'r') as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(1)
    return None
