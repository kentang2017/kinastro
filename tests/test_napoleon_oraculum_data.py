from astro.napoleon_oraculum.data import (
    ORACULUM_LETTERS,
    answers,
    get_oraculum_answer,
    oraculum,
    question_pairs,
    questions,
)


def test_oraculum_shapes() -> None:
    assert len(questions) == 16
    assert len(question_pairs) == 16
    assert len(oraculum) == 16
    assert all(len(row) == 16 for row in oraculum)


def test_answers_tables_complete() -> None:
    for key in ORACULUM_LETTERS:
        assert key in answers
        assert len(answers[key]) == 16


def test_lookup_works_with_inverted_a_slot() -> None:
    result = get_oraculum_answer(question_index=1, number_index=15)
    assert result["letter"] == "Ɐ"
    assert result["answer"] == answers["Ɐ"][15]
