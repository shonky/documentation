#!/usr/bin/env python3

import fnmatch
import logging
import os
import subprocess

import sh

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def touch(name):
    open(name, 'a').close()


def is_git_change(lang):
    """
    Determines if a git file has changed since the last push that is in the checklist
    :rtype: bool
    """
    check_list = [
      f"content/{lang}/*",
      f"i18n/{lang}.json",
      "data/*",
      "config/*",
      "layouts/*"
    ]
    CI_COMMIT_BEFORE_SHA = os.environ.get('CI_COMMIT_BEFORE_SHA', '')
    CI_COMMIT_SHA = os.environ.get('CI_COMMIT_SHA', '')
    git = sh.git.bake(_tty_out=False)

    before_exists = rev_exists(CI_COMMIT_BEFORE_SHA)
    now_exists = rev_exists(CI_COMMIT_SHA)
    logger.info(f'Hash {CI_COMMIT_BEFORE_SHA} exists = {before_exists}')
    logger.info(f'Hash {CI_COMMIT_SHA} exists = {now_exists}')

    if not before_exists:
        # Previous commit hash doesn't exist! this might have been a rebase and force push
        # Better to assume there are changes
        return True
    else:
        try:
            diff = git.diff('--name-only', f"{CI_COMMIT_BEFORE_SHA}...{CI_COMMIT_SHA}").split('\n')
        except sh.ErrorReturnCode as e:
            diff = []
            logger.error("diffing error", exc_info=1)
            print(e.full_cmd)
            print(e.stderr)

        for file_name in diff:
            for check_item in check_list:
                if fnmatch.fnmatch(file_name, check_item):
                    logger.info(f'match on {file_name} to {check_item}')
                    return True
        return False


def is_placeholder_change(lang):
    """
    Determines if a placeholder file changed
    :rtype: bool
    """
    git = sh.git.bake(_tty_out=False)
    for _ in git("ls-files", "--others", f"./content/{lang}/"):
        logger.info(f'match on {_}')
        return True
    return False


def rev_exists(rev):
    return not subprocess.call(('git', 'rev-list', '--quiet', rev))


def main():
    """
    loop over languages and check if a git file changed or placeholder changed in that language
    if it did then create a file called 'continue' appended with the language.
    We can then pass this file to other gitlab jobs and using its existence determine if we should execute other code.
    """
    languages = os.environ.get('LANGUAGES', '')
    languages = languages.split(",") if languages else []
    for lang in languages:
        if is_git_change(lang) or is_placeholder_change(lang):
            logger.info(f"Changes detected for {lang}..")
            touch(f"continue_{lang}")


if __name__ == '__main__':
    main()
