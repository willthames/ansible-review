from ansiblelint import AnsibleLintRule


class TestTaskSuccessRule(AnsibleLintRule):
    id = 'TEST0002'
    shortdesc = 'Test success rule for ansible-review tasks - always succeeds'
    description = 'Always fails'
    tags = ['deprecated']

    def matchtask(self, file, task):
        return False
