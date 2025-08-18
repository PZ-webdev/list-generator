import os
from typing import List, Optional
import config

from app.dto.branch import Branch
from app.utils.file_utils import read_json_utf8, write_json_utf8


def _read_is_old_global() -> bool:
    try:
        data = read_json_utf8(config.SETTINGS_FILE)
        if isinstance(data, dict):
            return bool(data.get("is_old_pigeon", False))
    except Exception:
        pass
    return True


class BranchService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.branches: List[Branch] = self.load_branches()

    def load_branches(self) -> List[Branch]:
        if os.path.exists(self.file_path):
            data = read_json_utf8(self.file_path)
            return [Branch.from_dict(item) for item in (data or [])]
        return []

    def save_branches(self):
        write_json_utf8([b.to_dict() for b in self.branches], self.file_path)

    def get_all(self, *, only_current_season: bool = False) -> List[Branch]:
        if not only_current_season:
            return self.branches
        current_is_old = _read_is_old_global()
        return [b for b in self.branches if bool(getattr(b, "is_old_pigeon", False)) == current_is_old]

    def get_by_season(self, is_old_pigeon: bool) -> List[Branch]:
        return [b for b in self.branches if bool(getattr(b, "is_old_pigeon", False)) == is_old_pigeon]

    def add_branch(
        self,
        name: str,
        number: str,
        input_path: str,
        output_path: str,
        is_old_pigeon: Optional[bool] = True
    ):

        if is_old_pigeon is None:
            is_old_pigeon = _read_is_old_global()

        next_id = str(max([int(b.id) for b in self.branches], default=0) + 1)
        new_branch = Branch(
            id=next_id,
            name=name,
            number=number,
            input=input_path,
            output=output_path,
            is_old_pigeon=bool(is_old_pigeon),
        )
        self.branches.append(new_branch)
        self.save_branches()

    def delete_branch(self, branch_id: str):
        self.branches = [b for b in self.branches if b.id != branch_id]
        self.save_branches()

    def update_branch(self, updated: Branch):
        self.delete_branch(updated.id)
        self.branches.append(updated)
        self.save_branches()
