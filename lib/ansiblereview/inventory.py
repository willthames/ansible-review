import ansible.inventory
from ansiblereview import Result, Inventory, utils
import yaml

try:
    import ansible.parsing.dataloader
    import ansible.vars
    ANSIBLE = 2
except ImportError:
    ANSIBLE = 1


def no_vars_in_host_file(inventory, options):
    errors = []
    with open(inventory, 'r') as f:
        try:
            yaml.safe_load(f)
        except Exception, e:
            for (line, lineno) in enumerate(f):
                if line.contains(':vars]'):
                    errors.append("line %s: contains a vars definition" % lineno)
    result = Result()
    if errors:
        result.stderr = '\n'.join(errors)
        result.failed = True
    return result


def parse(inventory, options):
    result = Result()
    try:
        if ANSIBLE > 1:
            loader = ansible.parsing.dataloader.DataLoader()
            var_manager = ansible.vars.VariableManager()
            ansible.inventory.Inventory(loader=loader, variable_manager=var_manager, host_list=inventory)
        else:
            ansible.inventory.Inventory(inventory)
    except Exception, e:
        result.stderr = "Inventory is broken: %s" % e.message
        result.failed = True
    return result


def review(inventoryfile, settings):
    return utils.review(Inventory(inventoryfile), settings)
