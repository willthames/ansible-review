from ansiblereview import Result, Error
from ansible.errors import AnsibleError
from ansiblereview.inventory import InventoryManager
import os

_vars = dict()
_inv = None


def remove_inherited_and_overridden_vars(vars, group, inventory):
    if group not in _vars:
        _vars[group] = inventory.get_group_vars(group)
    gv = _vars[group]
    for (k, v) in vars.items():
        if k in gv:
            try:
                if gv[k] == v:
                    vars.pop(k)
                else:
                    gv.pop(k)
            except AnsibleError:
                gv.pop(k)


def remove_inherited_and_overridden_group_vars(group, inventory):
    if group not in _vars:
        _vars[group] = inventory.get_group_vars(group)
    for ancestor in group.get_ancestors():
        remove_inherited_and_overridden_vars(_vars[group], ancestor, inventory)


def same_variable_defined_in_competing_groups(candidate, options):
    result = Result(candidate.path)
    # assume that group_vars file is under an inventory *directory*
    global _inv
    invfile = os.path.dirname(os.path.dirname(candidate.path))
    groupname = os.path.basename(candidate.path)
    if invfile.endswith('group_vars'):
        invfile = os.path.dirname(invfile)
        groupname = os.path.basename(os.path.dirname(candidate.path))

    try:
        inv = _inv or InventoryManager(invfile).inventory
        _inv = inv
    except AnsibleError as e:
        result.errors = [Error(None, "Inventory is broken: %s" % e.message)]
        return result

    group = inv.get_group(groupname)
    if not group:
        # group file exists in group_vars but no related group
        # in inventory directory
        return result
    remove_inherited_and_overridden_group_vars(group, inv)
    group_vars = set(_vars[group].keys())
    child_hosts = group.hosts
    child_groups = group.child_groups
    siblings = set()

    for child_host in child_hosts:
        siblings.update(child_host.groups)
    for child_group in child_groups:
        siblings.update(child_group.parent_groups)
    for sibling in siblings:
        if sibling != group:
            remove_inherited_and_overridden_group_vars(sibling, inv)
            sibling_vars = set(_vars[sibling].keys())
            common_vars = sibling_vars & group_vars
            common_hosts = [host.name for host in set(child_hosts) & set(sibling.hosts)]
            if common_vars and common_hosts:
                for var in common_vars:
                    error_msg_template = "Sibling groups {0} and {1} with common hosts {2} " + \
                                         "both define variable {3}"
                    error_msg = error_msg_template.format(group.name, sibling.name,
                                                          ", ".join(common_hosts), var)
                    result.errors.append(Error(None, error_msg))

    return result
