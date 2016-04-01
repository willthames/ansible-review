import ansible.constants as C
import ansible.inventory
import sys

try:
    import ansible.parsing.dataloader
    import ansible.vars
    ANSIBLE = 2
except ImportError:
    ANSIBLE = 1

try:
    if ANSIBLE > 1:
        loader = ansible.parsing.dataloader.DataLoader()
        var_manager = ansible.vars.VariableManager()
        im = ansible.inventory.Inventory(loader=loader, variable_manager=var_manager, host_list=C.DEFAULT_HOST_LIST)
    else:
        im = ansible.inventory.Inventory(C.DEFAULT_HOST_LIST)
except Exception, e:
    raise SystemExit("Inventory is broken: ", e.message)

sys.exit(0)
