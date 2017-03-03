import codecs
import os
import yaml

from ansiblereview import Result, Error


def yamlrolesfile(candidate, settings):
    rolesfile = os.path.join(os.path.dirname(candidate.path), "rolesfile")
    result = Result(candidate)
    if os.path.exists(rolesfile) and not os.path.exists(rolesfile + ".yml"):
        result.errors = [Error(None, "Rolesfile %s does not "
                                     "have a .yml extension" % rolesfile)]
        return result
    rolesfile = os.path.join(os.path.dirname(candidate.path), "rolesfile.yml")
    if os.path.exists(rolesfile):
        with codecs.open(rolesfile, mode='rb', encoding='utf-8') as f:
            try:
                yaml.safe_load(f)
            except Exception as e:
                result.errors = [Error(None, "Cannot parse YAML from %s: %s" %
                                       (rolesfile, str(e)))]
    return result
