import ansible.inventory
from ansiblereview import Result, Error
import codecs
import yaml

try:
    import ansible.parsing.dataloader
except ImportError:
    ANSIBLE = 1
else:
    ANSIBLE = 2
    try:
        from ansible.vars.manager import VariableManager
    except ImportError:
        from ansible.vars import VariableManager
    if not hasattr(ansible.inventory, 'Inventory'):
        # The inventory system was reworked in Ansible 2.4.
        import ansible.inventory.manager
        ANSIBLE = 2.4


def no_vars_in_host_file(candidate, options):
    errors = []
    with codecs.open(candidate.path, mode='rb', encoding='utf-8') as f:
        try:
            yaml.safe_load(f)
        except Exception:
            for (lineno, line) in enumerate(f):
                if ':vars]' in line:
                    errors.append(Error(lineno + 1, "contains a vars definition"))
    return Result(candidate.path, errors)


def parse(candidate, options):
    result = Result(candidate.path)
    try:
        if ANSIBLE > 1:
            loader = ansible.parsing.dataloader.DataLoader()
            if ANSIBLE > 2:
                inventory = ansible.inventory.manager.InventoryManager(
                    sources=candidate.path,
                    loader=loader,
                )
                VariableManager(loader=loader, inventory=inventory)
            else:
                var_manager = VariableManager()
                ansible.inventory.Inventory(loader=loader,
                                            variable_manager=var_manager,
                                            host_list=candidate.path)
        else:
            ansible.inventory.Inventory(candidate.path)
    except Exception as e:
        if hasattr(e, 'message'):
            message = e.message
        else:
            message = str(e)
        result.errors = [Error(None, "Inventory is broken: %s" % message)]
    return result
