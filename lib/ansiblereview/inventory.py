from ansible import constants
from ansiblereview import Result, Error
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
import ansible.inventory.manager
import codecs
import yaml


class NoVaultSecretFound(Exception):
    pass


class AnsibleInventory(object):

    def __init__(self, inventory, ask_vault_pass, vault_password_files, vault_ids):
        from ansible.cli import CLI
        super(AnsibleInventory, self).__init__()
        loader = DataLoader()
        if vault_ids or vault_password_files or ask_vault_pass:
            CLI.setup_vault_secrets(loader, vault_ids, vault_password_files, ask_vault_pass)
        self.inventory = ansible.inventory.manager.InventoryManager(loader=loader,
                                                                    sources=inventory)
        self.variable_manager = VariableManager(loader=loader)
        self.variable_manager.set_inventory(self.inventory)

    # internal fuctions that actually do the work
    # adapted almost entirely from lib/ansible/vars/manager.py
    def _plugins_inventory(self, entities):
        import os
        from ansible.plugins.loader import vars_loader
        from ansible.utils.vars import combine_vars
        ''' merges all entities by inventory source '''
        data = {}
        for inventory_dir in self.variable_manager._inventory._sources:
            if ',' in inventory_dir:  # skip host lists
                continue
            elif not os.path.isdir(inventory_dir):  # always pass 'inventory directory'
                inventory_dir = os.path.dirname(inventory_dir)

            for plugin in vars_loader.all():
                data = combine_vars(data, self._get_plugin_vars(plugin, inventory_dir, entities))
        return data

    def _get_plugin_vars(self, plugin, path, entities):
        from ansible.inventory.host import Host
        data = {}
        try:
            data = plugin.get_vars(self.variable_manager._loader, path, entities)
        except AttributeError:
            for entity in entities:
                if isinstance(entity, Host):
                    data.update(plugin.get_host_vars(entity.name))
                else:
                    data.update(plugin.get_group_vars(entity.name))
        return data

    def get_group_vars(self, group):
        return self._plugins_inventory([group])

    def get_host_vars(self, host):
        try:
            all_vars = self.variable_manager.get_vars(host=host, include_hostvars=True)
        except ansible.errors.AnsibleParserError:
            raise NoVaultSecretFound
        # play, host, task, include_hostvars, include_delegate_to
        magic_vars = ['ansible_playbook_python', 'groups', 'group_names', 'inventory_dir',
                      'inventory_file', 'inventory_hostname', 'inventory_hostname_short',
                      'omit', 'playbook_dir']
        return {k: v for (k, v) in all_vars.items() if k not in magic_vars}

    def get_group(self, group_name):
        return self.inventory.groups.get(group_name)


class InventoryManager(object):
    def __init__(self, inventory, ask_vault_pass=False, vault_password_files=None, vault_ids=None):

        if not vault_password_files:
            vault_password_files = []
            if constants.DEFAULT_VAULT_PASSWORD_FILE:
                vault_password_files.append(constants.DEFAULT_VAULT_PASSWORD_FILE)
        if not vault_ids:
            vault_ids = []
        self.inventory = AnsibleInventory(inventory, ask_vault_pass,
                                          vault_password_files, vault_ids)


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
        InventoryManager(candidate.path)
    except Exception as e:
        result.errors = [Error(None, "Inventory is broken: %s" % str(e))]
    return result
