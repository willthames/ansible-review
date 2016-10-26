from ansiblelint import AnsibleLintRule


class FileContainsContentRule(AnsibleLintRule):
    id = 'EXTRA0011'
    shortdesc = 'all files should contain useful content'
    description = 'Having effectively empty YAML files is purposeless'
    tags = ['leastsurprise']

    def matchplay(self, file, data):
        if not data:
            return [({file.type: data}, self.shortdesc)]

