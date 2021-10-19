#!/usr/bin/env python3
"""Executable script to pass to git filter-branch --msgfilter to rewrite trailers.

This treats everything (stdin, stdout, env) at the level of raw bytes which are
assumed to be utf-8, or more specifically some ASCII superset, regardless of
(possibly broken) LOCALE settings.

"""
import collections
import os
import re
import sys

STDIN = sys.stdin.buffer
STDOUT = sys.stdout.buffer
STDERR = sys.stderr.buffer


def die(msg):
    STDERR.write(b'ERROR: ')
    STDERR.write(msg)
    sys.exit(1)


def drop_trailing_newlines(lines):
    while lines and not lines[-1]:
        del lines[-1]


def remove_duplicates(trailers):
    return list(collections.OrderedDict((t, None) for t in trailers).keys())


def rework_commit_message(commit_message, value):
    if not commit_message:
        die(b'Expected a non-empty commit message')

    trailer_name = b'Signed-off-by:'
    trailer = trailer_name + b' ' + value
    reworked_lines = [line.rstrip() for line in commit_message.split(b'\n')]

    drop_trailing_newlines(reworked_lines)

    if trailer_name in reworked_lines[-1]:
        del reworked_lines[-1]
    if trailer not in reworked_lines:
        reworked_lines.append(trailer)

    drop_trailing_newlines(reworked_lines)

    return b'\n'.join(reworked_lines)


def main():
    sob = os.environb[b'SOB']
    original_commit_message = STDIN.read().strip()
    new_commit_message = rework_commit_message(original_commit_message, sob)
    STDOUT.write(new_commit_message)


if __name__ == '__main__':
    main()
