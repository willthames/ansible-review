from ansiblelint import AnsibleLintRule


class TestPlaySuccessRule(AnsibleLintRule):
    id = 'TEST0004'
    shortdesc = 'Test success rule for ansible-review plays - always succeeds'
    description = 'Always succeeds'
    tags = ['deprecated']

    def matchplay(self, file, play):
        return False
