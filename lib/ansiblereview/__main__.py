#!/usr/bin/env python

from __future__ import print_function
import logging
import optparse
import os
import sys
from ansiblereview.version import __version__
from ansiblereview import classify
from ansiblereview.utils import info, warn, read_config
from appdirs import AppDirs
from pkg_resources import resource_filename


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
    config_dir = AppDirs("ansible-review", "com.github.willthames").user_config_dir
    default_config_file = os.path.join(config_dir, "config.ini")

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
    parser.add_option('-y', dest='indent_list_items', action="store_true",
                      help="Whether YAML lists should be indented")

    options, args = parser.parse_args(sys.argv[1:])
    settings = read_config(options.configfile)

    # Merge CLI options with config options. CLI options override config options.
    for key, value in settings.__dict__.items():
        if not getattr(options, key):
            setattr(options, key, getattr(settings, key))

    if os.path.exists(options.configfile):
        info("Using configuration file: %s" % options.configfile, options)
    else:
        warn("No configuration file found at %s" % options.configfile, options, file=sys.stderr)
        if not options.rulesdir:
            rules_dir = os.path.join(resource_filename('ansiblereview', 'examples'))
            warn("Using example standards found at %s" % rules_dir, options, file=sys.stderr)
            options.rulesdir = rules_dir
        if not options.lintdir:
            lint_dir = os.path.join(options.rulesdir, 'lint-rules')
            if os.path.exists(lint_dir):
                warn("Using example lint-rules found at %s" % lint_dir, options, file=sys.stderr)
                options.lintdir = lint_dir

    if len(args) == 0:
        buf = sys.stdin
        if sys.version_info[0] == 3:
            """Bypass bytes to unidiff regardless."""
            buf = buf.buffer
        candidates = get_candidates_from_diff(buf)
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
                warn("Not reviewing binary file %s" % filename, options)
                continue
            if lines:
                info("Reviewing %s lines %s" % (candidate, lines), options)
            else:
                info("Reviewing all of %s" % candidate, options)
            errors = errors + candidate.review(options, lines)
        else:
            info("Couldn't classify file %s" % filename, options)
    return errors
