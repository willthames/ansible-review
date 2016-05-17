import codecs
import yaml
from yaml.composer import Composer
from ansiblereview import Result, Error


def hunt_repeated_yaml_keys(data):
    """Parses yaml and returns a list of repeated variables and
       the line on which they occur
    """
    loader = yaml.Loader(data)

    def compose_node(parent, index):
        # the line number where the previous token has ended (plus empty lines)
        line = loader.line
        node = Composer.compose_node(loader, parent, index)
        node.__line__ = line + 1
        return node

    def construct_mapping(node, deep=False):
        mapping = dict()
        errors = dict()
        for key_node, value_node in node.value:
            key = key_node.value

            if key in mapping:
                errors[key] = node.__line__

            value = value_node.value
            mapping[key] = value

        return errors

    loader.compose_node = compose_node
    loader.construct_mapping = construct_mapping
    data = loader.get_single_data()
    return data


def repeated_vars(candidate, settings):
    with codecs.open(candidate.path, 'r') as text:
        errors = hunt_repeated_yaml_keys(text) or dict()
    return Result([Error(errors[err], "Variable %s occurs more than once" % err) for
                   err in errors])
