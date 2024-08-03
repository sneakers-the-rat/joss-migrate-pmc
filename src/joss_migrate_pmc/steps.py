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



STEPS = [rename_directory]





