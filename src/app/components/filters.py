from __future__ import annotations


def to_options(values: list[str]) -> list[dict]:
	unique_values = []
	seen = set()
	for v in values:
		if v in seen:
			continue
		seen.add(v)
		unique_values.append(v)
	return [{"label": v, "value": v} for v in unique_values]


def move_option_to_end(options: list[dict], value_to_move: str) -> list[dict]:
	kept = [o for o in options if o.get("value") != value_to_move]
	moved = [o for o in options if o.get("value") == value_to_move]
	return kept + moved
