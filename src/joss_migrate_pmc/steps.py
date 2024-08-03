import pdb
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import re
import subprocess

from joss_migrate_pmc.paper import JossPaper

ORIGINAL_NAME = re.compile(r'joss.\d{5}')

@dataclass
class Result:
    success: bool
    path: Path
    value: Optional[str] = None
    error: Optional[str] = None


def _git_mv(repo_dir: Path, source:Path, target:Path) -> subprocess.CompletedProcess:
    res = subprocess.run(['git', '-C', str(repo_dir.resolve()), 'mv', str(source.resolve()),
                          str(target.resolve())], capture_output=True)
    return res


def rename_directory(path: Path) -> Result:
    """
    Step 0: change paper directory from `joss.uid` -> `joss-vol-uid`
    """
    if not ORIGINAL_NAME.match(path.name):
        # already renamed this one
        return Result(success=True, path=path)

    paper = JossPaper(path=path)
    new_directory = f"joss-{paper.volume}-{paper.uid}"

    res = subprocess.run(['git', '-C', str(path.parent), 'mv', str(path.resolve()), str(path.resolve().parent / new_directory)], capture_output=True)
    if res.returncode != 0:
        res = Result(success=False, path=path, error=str(res.stderr))
    else:
        res = Result(success=True, path=path, value=new_directory)
    return res

def unnest_jats(path: Path) -> Result:
    """
    Step 1: Unnest `paper.jats` directories to put JATS xml in the root.

    Leave media in place for now, will be moved in future steps that
    update the JATS locations.

    Also postpone renaming to `.xml` , will handle in a later step because
    some old files have
    """
    jats_subdir = path / 'paper.jats'
    if not jats_subdir.exists():
        return Result(success=True, path=path, value="No jats subdirectory")
    new_file = None
    for jats_file in jats_subdir.glob('*.jats'):
        new_file = path / jats_file.name
        res = _git_mv(path.parent, jats_file, new_file)
        if res.returncode != 0:
            return Result(success=False, path=path, error=str(res.stderr))
    if new_file is None:
        return Result(success=False, path=path, value="No jats files")
    else:
        return Result(success=True, path=path, value=str(new_file))



STEPS = [rename_directory, unnest_jats]





