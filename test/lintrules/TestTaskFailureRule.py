from ansiblelint import AnsibleLintRule


class TestTaskFailureRule(AnsibleLintRule):
    id = 'TEST0001'
    shortdesc = 'Test failure rule for ansible-review tasks - always fails'
    description = 'Always fails'
    tags = ['deprecated']

    def matchtask(self, file, task):
        return True
