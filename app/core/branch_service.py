import json
import os
from typing import List, Dict


class BranchService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.branches: List[Dict] = self.load_branches()

    def load_branches(self) -> List[Dict]:
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_branches(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.branches, f, indent=4, ensure_ascii=False)

    def get_all(self) -> List[Dict]:
        return self.branches

    def add_branch(self, name: str, input_path: str, output_path: str):
        next_id = str(max([int(b['id']) for b in self.branches], default=0) + 1)
        new_branch = {'id': next_id, 'name': name, 'input': input_path, 'output': output_path}
        self.branches.append(new_branch)
        self.save_branches()

    def delete_branch(self, branch_id: str):
        self.branches = [b for b in self.branches if b['id'] != branch_id]
        self.save_branches()

    def update_branch(self, updated_branch: Dict):
        self.delete_branch(updated_branch['id'])
        self.branches.append(updated_branch)
        self.save_branches()
