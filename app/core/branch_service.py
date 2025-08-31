import os
from typing import List, Optional
import config

from app.dto.branch import Branch
from app.utils.file_utils import read_json_utf8, write_json_utf8


class BranchService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.branches: List[Branch] = self.load_branches()

    def load_branches(self) -> List[Branch]:
        if os.path.exists(self.file_path):
            data = read_json_utf8(self.file_path)
            return [Branch.from_dict(item) for item in (data or [])]
        return []

    def save_branches(self) -> None:
        write_json_utf8([b.to_dict() for b in self.branches], self.file_path)

    def get_all(self) -> List[Branch]:
        return self.branches

    def add_branch(
            self,
            name: str,
            number: str,
            input_path: str,
            output_path: str
    ) -> None:
        next_id = str(max([int(b.id) for b in self.branches], default=0) + 1)
        new_branch = Branch(
            id=next_id,
            name=name,
            number=number,
            input=input_path,
            output=output_path
        )
        self.branches.append(new_branch)
        self.save_branches()

    def delete_branch(self, branch_id: str) -> None:
        self.branches = [b for b in self.branches if b.id != branch_id]
        self.save_branches()

    def update_branch(self, updated: Branch) -> None:
        # Replace in place to preserve order
        for idx, b in enumerate(self.branches):
            if b.id == updated.id:
                self.branches[idx] = updated
                self.save_branches()
                return
        # If not found, append as fallback
        self.branches.append(updated)
        self.save_branches()

    # Ordering helpers
    def _move(self, branch_id: str, offset: int) -> None:
        try:
            idx = next(i for i, b in enumerate(self.branches) if b.id == branch_id)
        except StopIteration:
            return
        new_idx = idx + offset
        if new_idx < 0 or new_idx >= len(self.branches):
            return
        item = self.branches.pop(idx)
        self.branches.insert(new_idx, item)
        self.save_branches()

    def move_up(self, branch_id: str) -> None:
        self._move(branch_id, -1)

    def move_down(self, branch_id: str) -> None:
        self._move(branch_id, 1)
