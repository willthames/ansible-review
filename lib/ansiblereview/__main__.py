#!/usr/bin/env python

from __future__ import print_function
import logging
import optparse
import os
import sys
from ansiblereview.version import __version__
from ansiblereview import classify
from ansiblereview.utils import read_config, get_default_config
from pkg_resources import resource_filename
from ansiblereview.display import load_display_handler

def get_candidates_from_diff(difftext):
    try:
        import unidiff
    except ImportError as e:
        raise SystemExit("Could not import unidiff library: %s", e.message)
    patch = unidiff.PatchSet(difftext, encoding='utf-8')

    candidates = []
    for patchedfile in [patchfile for patchfile in
                        patch.added_files + patch.modified_files]:
        if patchedfile.source_file == '/dev/null':
            candidates.append(patchedfile.path)
        else:
            lines = ",".join(["%s-%s" % (hunk.target_start, hunk.target_start + hunk.target_length)
                              for hunk in patchedfile])
            candidates.append("%s:%s" % (patchedfile.path, lines))
    return candidates


def main():
    default_config_file = get_default_config()
    parser = optparse.OptionParser("%prog playbook_file|role_file|inventory_file",
                                   version="%prog " + __version__)
    parser.add_option('-c', dest='configfile', default=default_config_file,
                      help="Location of configuration file: [%s]" % default_config_file)
    parser.add_option('-d', dest='rulesdir',
                      help="Location of standards rules")
    parser.add_option('-r', dest='lintdir',
                      help="Location of additional lint rules")
    parser.add_option('-q', dest='log_level', action="store_const", default=logging.WARN,
                      const=logging.ERROR, help="Only output errors")
    parser.add_option('-s', dest='standards_filter', action='append',
                      help="limit standards to specific names")
    parser.add_option('-v', dest='log_level', action="store_const", default=logging.WARN,
                      const=logging.INFO, help="Show more verbose output")
    
    options, args = parser.parse_args(sys.argv[1:])
    settings = read_config(options.configfile)

    display = load_display_handler('default', __name__, options.log_level)
    
    # Merge CLI options with config options. CLI options override config options.
    for key, _ in settings.__dict__.items():
        if not getattr(options, key):
            setattr(options, key, getattr(settings, key))

    if os.path.exists(options.configfile):
        display.info("Using configuration file: %s" % options.configfile, options)
    else:
        display.warn("No configuration file found at %s" % options.configfile)
        if not options.rulesdir:
            rules_dir = os.path.join(resource_filename('ansiblereview', 'examples'))
            display.warn("Using example standards found at %s" % rules_dir)
            options.rulesdir = rules_dir
        if not options.lintdir:
            lint_dir = os.path.join(options.rulesdir, 'lint-rules')
            if os.path.exists(lint_dir):
                display.warn("Using example lint-rules found at %s" % lint_dir)
                options.lintdir = lint_dir

    if len(args) == 0:
        candidates = get_candidates_from_diff(sys.stdin)
    else:
        candidates = args

    errors = 0
    for filename in candidates:
        if ':' in filename:
            (filename, lines) = filename.split(":")
        else:
            lines = None
        candidate = classify(filename)
        if candidate:
            if candidate.binary:
                display.warn("Not reviewing binary file %s" % filename)
                continue
            if lines:
                display.info("Reviewing %s lines %s" % (candidate, lines))
            else:
                display.info("Reviewing all of %s" % candidate)
            errors = errors + candidate.review(options, lines, display=display)
        else:
            display.info("Couldn't classify file %s" % filename)
    return errors
