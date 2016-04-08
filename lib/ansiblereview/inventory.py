import ansible.inventory
from ansiblereview import Result
import yaml

try:
    import ansible.parsing.dataloader
    import ansible.vars
    ANSIBLE = 2
except ImportError:
    ANSIBLE = 1


def no_vars_in_host_file(candidate, options):
    errors = []
    with open(candidate.path, 'r') as f:
        try:
            yaml.safe_load(f)
        except Exception, e:
            for (lineno, line) in enumerate(f):
                if ':vars]' in line:
                    errors.append("line %s: contains a vars definition" % lineno + 1)
    result = Result()
    if errors:
        result.stderr = '\n'.join(errors)
        result.failed = True
    return result


def parse(candidate, options):
    result = Result()
    try:
        if ANSIBLE > 1:
            loader = ansible.parsing.dataloader.DataLoader()
            var_manager = ansible.vars.VariableManager()
            ansible.inventory.Inventory(loader=loader, variable_manager=var_manager, host_list=candidate.path)
        else:
            ansible.inventory.Inventory(candidate.path)
    except Exception, e:
        result.stderr = "Inventory is broken: %s" % e.message
        result.failed = True
    return result
