from ansiblelint import AnsibleLintRule


class MetaMainHasEmptyDependenciesRule(AnsibleLintRule):
    id = 'EXTRA0012'
    shortdesc = 'meta/main.yml should not declare dependencies'
    description = 'Dependencies hurt the ability to maintain versioned roles'
    tags = ['dependencies']

    def matchplay(self, file, data):
        if 'dependencies' not in data or data['dependencies']:
            return [({'meta/main.yml': data}, self.shortdesc)]
