"""Offline unit tests for council ranking behavior."""

from backend.council import calculate_aggregate_rankings, parse_ranking_from_text


def test_final_ranking_keeps_only_first_occurrence_of_each_label():
    ranking = """Evaluation text.

FINAL RANKING:
1. Response C
2. Response A
3. Response C
4. Response B
5. Response A
"""

    assert parse_ranking_from_text(ranking) == [
        "Response C",
        "Response A",
        "Response B",
    ]


def test_fallback_ranking_keeps_only_first_occurrence_of_each_label():
    ranking = "I prefer Response B over Response A; Response B is best."

    assert parse_ranking_from_text(ranking) == ["Response B", "Response A"]


def test_aggregate_counts_each_model_once_per_judgment():
    ranking = "I prefer Response B over Response A; Response B is best."
    aggregate = calculate_aggregate_rankings(
        [{"model": "judge", "ranking": ranking}],
        {"Response A": "model-a", "Response B": "model-b"},
    )

    assert aggregate == [
        {"model": "model-b", "average_rank": 1.0, "rankings_count": 1},
        {"model": "model-a", "average_rank": 2.0, "rankings_count": 1},
    ]
    assert aggregate[0]["average_rank"] < aggregate[1]["average_rank"]
