from ansiblereview import utils, Role


def review(rolesdir, settings):
    return utils.review(Role(rolesdir), settings)
