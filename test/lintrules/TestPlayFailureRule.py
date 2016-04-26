from ansiblelint import AnsibleLintRule


class TestPlayFailureRule(AnsibleLintRule):
    id = 'TEST0003'
    shortdesc = 'Test failure rule for ansible-review plays - always fails'
    description = 'Always fails'
    tags = ['deprecated']

    def matchplay(self, file, play):
        return True
