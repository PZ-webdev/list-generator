import os
import re
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Optional, Set, Tuple

from app.dto.settings_dto import SettingsDTO
from app.utils.file_utils import read_file_cp852
from app.utils.logger import log_info


@dataclass
class CompetitionRow:
    position: int
    breeder: str
    branch: str
    lot_type: str
    points: Decimal


@dataclass
class AggregatedRow:
    breeder: str
    branch: str
    lot_type: str
    positions: List[int]
    points: Decimal

    @property
    def count(self) -> int:
        return len(self.positions)


class RankingService:
    """Generuje ranking drużynowy na podstawie listy konkursowej WSP_LKON."""

    DEFAULT_TOP_LIMIT = 5

    _HEADER_LINES: Tuple[str, ...] = (
        "",
        "",
        "                NAJLEPSZE DRUZYNY Z LOTU ",
        "",
        " ┌───┬─────────────────────────────┬──┬──────────────────────────┬────────┐",
        " │Lp.│ NAZWISKO HODOWCY        DR. │K.│ POZYCJE GOŁĘBI NA LISCIE │ PUNKTY │",
        " ├───┼─────────────────────────────┼──┼──────────────────────────┼────────┤",
    )

    _CONTROL_CHARS = ("\x1b", "\x0f", "\x02", "\x0c")

    def generate_scoreboard(
        self,
        wsp_path: str,
        allowed_types: Optional[Iterable[str]] = None,
        top_limit: int = DEFAULT_TOP_LIMIT,
    ) -> str:
        if not os.path.isfile(wsp_path):
            raise FileNotFoundError("Nie odnaleziono wskazanego pliku WSP_LKON.TXT.")

        raw_content = read_file_cp852(wsp_path)
        sanitized = self._sanitize_text(raw_content)

        allowed_set = None
        if allowed_types:
            allowed_set = {value.strip().upper() for value in allowed_types if value}
            if not allowed_set:
                allowed_set = None

        normalized_limit = self._normalize_top_limit(top_limit)

        rows = list(self._extract_rows(sanitized, allowed_set))
        if not rows:
            raise ValueError("Nie udało się odnaleźć wyników konkursowych w pliku.")

        aggregated = self._aggregate(rows, normalized_limit)
        output_dir = self._resolve_output_dir(wsp_path)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, 'Punktacja.TXT')
        rendered_lines = self._render_lines(aggregated, normalized_limit)
        payload = '\r\n'.join(rendered_lines) + '\r\n'

        with open(output_path, 'w', encoding='cp852', newline='') as handle:
            handle.write(payload)

        log_info(f'Zapisano ranking drużyn do pliku: {output_path}')
        return output_path

    def _sanitize_text(self, text: str) -> str:
        sanitized = text.replace('\r\n', '\n').replace('\r', '\n')
        for char in self._CONTROL_CHARS:
            sanitized = sanitized.replace(char, '')
        return sanitized

    def _extract_rows(
        self,
        text: str,
        allowed_types: Optional[Set[str]] = None,
    ) -> Iterable[CompetitionRow]:
        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            if len(line) < 60 or 'PL-' not in line:
                continue

            position_segment = line[:5].strip()
            if not position_segment.isdigit():
                continue

            breeder = line[5:29].strip()
            if not breeder:
                continue

            branch_field = line[29:35]
            match = re.search(r'\d{2,3}', branch_field)
            if not match:
                continue
            branch = match.group(0)

            lot_type = line[42:44].strip().upper() if len(line) >= 44 else ''
            if not lot_type.isalpha() or lot_type == '-':
                continue

            if allowed_types and lot_type not in allowed_types:
                continue

            if len(line) < 98:
                continue
            points_segment = line[90:98].strip()
            if not points_segment:
                continue

            try:
                points = Decimal(points_segment.replace(',', '.'))
            except Exception:
                continue

            yield CompetitionRow(
                position=int(position_segment),
                breeder=breeder,
                branch=branch,
                lot_type=lot_type,
                points=points,
            )

    def _aggregate(self, rows: Iterable[CompetitionRow], top_limit: int) -> List[AggregatedRow]:
        grouped: Dict[Tuple[str, str, str], List[CompetitionRow]] = defaultdict(list)
        for row in rows:
            grouped[(row.branch, row.breeder, row.lot_type)].append(row)

        aggregated: List[AggregatedRow] = []
        for (branch, breeder, lot_type), entries in grouped.items():
            sorted_entries = sorted(entries, key=lambda item: item.position)
            selected = sorted_entries[:top_limit]
            total = sum((entry.points for entry in selected), Decimal('0'))
            total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            aggregated.append(
                AggregatedRow(
                    breeder=breeder,
                    branch=branch,
                    lot_type=lot_type,
                    positions=[entry.position for entry in selected],
                    points=total,
                )
            )

        aggregated.sort(
            key=lambda item: (
                -item.count,
                -item.points,
                min(item.positions) if item.positions else 0,
                item.breeder,
                item.branch,
                item.lot_type,
            )
        )
        return aggregated

    def _normalize_top_limit(self, requested: int) -> int:
        try:
            value = int(requested)
        except (TypeError, ValueError):
            return self.DEFAULT_TOP_LIMIT

        if value < 1:
            return 1
        return value

    def _resolve_output_dir(self, wsp_path: str) -> str:
        try:
            settings = SettingsDTO.from_json()
            configured = settings.default_pdf_dir.strip()
            if configured and os.path.isdir(configured):
                return configured
        except Exception:
            pass
        return os.path.dirname(wsp_path)

    def _render_lines(self, aggregated: List[AggregatedRow], top_limit: int) -> List[str]:
        lines: List[str] = list(self._HEADER_LINES)

        for index, row in enumerate(aggregated, start=1):
            name = row.breeder[:23]
            padded_positions = (row.positions + [0] * top_limit)[:top_limit]
            raw_positions = ''.join(f"{pos:5d}" for pos in padded_positions)
            field_width = 5 * max(top_limit, self.DEFAULT_TOP_LIMIT)
            positions_segment = raw_positions.ljust(field_width)
            points_str = format(row.points, '.2f').replace('.', ',')
            line = (
                f"  {index:03d} "
                f"{name:<23}"
                f" {row.branch:>3} {row.lot_type}{row.count:4d}"
                f"{positions_segment}   {points_str:>7}"
            )
            lines.append(line.rstrip())

        lines.append('')
        return lines
