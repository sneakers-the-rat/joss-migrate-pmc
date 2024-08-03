import pdb
from dataclasses import dataclass
from pathlib import Path
from tqdm import tqdm

from joss_migrate_pmc.paper import JossPaper

@dataclass
class MissingFile:
    jats: str
    missing: str


def check_missing_files(paper:JossPaper) -> list[MissingFile]:
    if paper.jats_path is None:
        return []
    graphics = paper.jats.find_all('graphic')
    if not graphics:
        return []

    missing = []
    for graphic in graphics:
        rel_path = graphic.attrs['xlink:href']
        if not (paper.jats_path.parent / rel_path).exists() and not (paper.jats_path.parent / 'paper.jats' / rel_path).exists():
            missing.append(MissingFile(jats=str(paper.jats_path), missing=rel_path))
    return missing


def check_all_missing_files(repo: Path) -> list[MissingFile]:
    missing = []
    paper_dirs = list(repo.glob('joss*'))
    for paper_dir in tqdm(paper_dirs):
        try:
            paper = JossPaper(path=paper_dir)
            missing.extend(check_missing_files(paper))
        except Exception as e:
            pdb.post_mortem()
    return missing