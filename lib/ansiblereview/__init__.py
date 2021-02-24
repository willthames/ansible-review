try:
    from ansiblelint.constants import DEFAULT_RULESDIR
except ImportError:
    from ansiblelint import default_rulesdir as DEFAULT_RULESDIR
try:
    from ansiblelint.rules import RulesCollection
except ImportError:
    from ansiblelint import RulesCollection
import codecs
from functools import partial
import re
import os
from ansiblereview import utils

try:
    # Ansible 2.4 import of module loader
    from ansible.plugins.loader import module_loader
except ImportError:
    try:
        from ansible.plugins import module_loader
    except ImportError:
        from ansible.utils import module_finder as module_loader


RC_HAS_CREATE_FROM_DIR = hasattr(RulesCollection, "create_from_directory")


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
    def __init__(self, candidate, errors=None):
        self.candidate = candidate
        self.errors = errors or []

    def message(self):
        return "\n".join(["{0}:{1}".format(self.candidate, error)
                          for error in self.errors])


class Candidate(object):
    def __init__(self, filename):
        self.path = filename
        try:
            self.version = find_version(filename)
            self.binary = False
        except UnicodeDecodeError:
            self.binary = True
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
        role_modules = os.path.join(parentdir, 'library')
        if os.path.exists(role_modules):
            module_loader.add_directory(role_modules)


class Playbook(Candidate):
    pass


class Task(RoleFile):
    def __init__(self, filename):
        super(Task, self).__init__(filename)
        self.filetype = 'tasks'


class Handler(RoleFile):
    def __init__(self, filename):
        super(Handler, self).__init__(filename)
        self.filetype = 'handlers'


class Vars(Candidate):
    pass


class Unversioned(Candidate):
    def __init__(self, filename):
        super(Unversioned, self).__init__(filename)
        self.expected_version = False


class InventoryVars(Unversioned):
    pass


class HostVars(InventoryVars):
    pass


class GroupVars(InventoryVars):
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


# For ease of checking files for tabs
class Makefile(Unversioned):
    pass


class File(RoleFile):
    pass


class Rolesfile(Unversioned):
    pass


def classify(filename):
    parentdir = os.path.basename(os.path.dirname(filename))
    if parentdir in ['tasks']:
        return Task(filename)
    if parentdir in ['handlers']:
        return Handler(filename)
    if parentdir in ['vars', 'defaults']:
        return RoleVars(filename)
    if 'group_vars' in os.path.dirname(filename).split(os.sep):
        return GroupVars(filename)
    if 'host_vars' in os.path.dirname(filename).split(os.sep):
        return HostVars(filename)
    if parentdir == 'meta':
        return Meta(filename)
    if parentdir in ['library', 'lookup_plugins', 'callback_plugins',
                     'filter_plugins'] or filename.endswith('.py'):
        return Code(filename)
    if parentdir in ['inventory']:
        return Inventory(filename)
    if 'rolesfile' in filename or 'requirements' in filename:
        return Rolesfile(filename)
    if 'Makefile' in filename:
        return Makefile(filename)
    if 'templates' in filename.split(os.sep) or filename.endswith('.j2'):
        return Template(filename)
    if 'files' in filename.split(os.sep):
        return File(filename)
    if filename.endswith('.yml') or filename.endswith('.yaml'):
        return Playbook(filename)
    if 'README' in filename:
        return Doc(filename)
    return None


def lintcheck(rulename):
    return partial(ansiblelint, rulename)


def ansiblelint(rulename, candidate, settings):
    result = Result(candidate.path)
    rules = RulesCollection()
    if RC_HAS_CREATE_FROM_DIR:
        rules.extend(RulesCollection.create_from_directory(DEFAULT_RULESDIR))
        if settings.lintdir:
            rules.extend(RulesCollection.create_from_directory(settings.lintdir))
    else:
        rules.extend(RulesCollection([DEFAULT_RULESDIR]))
        if settings.lintdir:
            rules.extend(RulesCollection([settings.lintdir]))

    fileinfo = dict(path=candidate.path, type=candidate.filetype)
    matches = rules.run(fileinfo, rulename.split(','))
    result.errors = [Error(match.linenumber, "[%s] %s" % (match.rule.id, match.message))
                     for match in matches]
    return result


def find_version(filename, version_regex=r"^# Standards: ([0-9]+\.[0-9]+)"):
    version_re = re.compile(version_regex)
    with codecs.open(filename, mode='rb', encoding='utf-8') as f:
        for line in f:
            match = version_re.match(line)
            if match:
                return match.group(1)
    return None
