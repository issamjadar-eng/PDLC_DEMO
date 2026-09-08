"""JSON extraction — the behaviour that prevents a fail-open parse."""

from __future__ import annotations

import json

from multimodel import jsonx


def test_finds_bare_object():
    assert jsonx.best_object('{"ok": true}') == {"ok": True}


def test_ignores_braces_inside_strings():
    raw = '{"note": "uses {braces} and \\"quotes\\"", "ok": true}'
    assert jsonx.best_object(raw)["ok"] is True


def test_strips_code_fences():
    assert jsonx.best_object('```json\n{"ok": false}\n```') == {"ok": False}


def test_descends_into_string_envelope():
    """The Grok CLI shape: a {"text": "..."} wrapper around the real payload."""
    inner = '{"verdict": "yes", "score": 1}'
    assert jsonx.best_object(json.dumps({"text": inner}), "verdict")["score"] == 1


def test_last_object_wins_in_a_stream():
    """Agentic CLIs emit interim status objects, then the real answer last."""
    stream = (
        '{"verdict": "pending", "score": 0}'
        '{"verdict": "pending", "score": 0}'
        '{"verdict": "final", "score": 9}'
    )
    assert jsonx.best_object(stream, "verdict")["score"] == 9


def test_streamed_objects_inside_an_envelope():
    """Both quirks at once — the exact shape that caused the original bug."""
    inner = (
        '{"verdict": "working", "score": 0}'
        '{"verdict": "done", "score": 7, "note": "real answer"}'
    )
    found = jsonx.best_object(json.dumps({"text": inner}), "verdict")
    assert found["score"] == 7


def test_required_key_filters_out_the_envelope():
    payload = json.dumps({"metadata": "irrelevant", "text": '{"verdict": "x"}'})
    assert jsonx.best_object(payload, "verdict") == {"verdict": "x"}


def test_returns_none_when_nothing_matches():
    assert jsonx.best_object('{"unrelated": 1}', "verdict") is None


def test_returns_none_on_prose():
    assert jsonx.best_object("the model apologises and returns prose") is None


def test_returns_none_on_empty():
    assert jsonx.best_object("") is None


def test_surrounding_prose_is_skipped_not_fatal():
    raw = 'Sure! Here is my answer:\n{"verdict": "ok"}\nHope that helps.'
    assert jsonx.best_object(raw, "verdict") == {"verdict": "ok"}


def test_invalid_object_among_valid_ones_is_skipped():
    raw = '{not valid json}{"verdict": "ok"}'
    assert jsonx.best_object(raw, "verdict") == {"verdict": "ok"}


def test_truncated_wrapper_yields_nothing():
    """An unterminated object has no balanced span — fails closed on purpose."""
    assert jsonx.best_object('{"broken": {"verdict": "ok"}', "verdict") is None


def test_iter_json_objects_counts_correctly():
    assert len(jsonx.iter_json_objects('{"a":1}{"b":{"c":2}}{"d":3}')) == 3


def test_first_required_key_prefers_required_then_properties():
    assert jsonx.first_required_key({"required": ["b", "a"], "properties": {"a": {}}}) == "b"
    assert jsonx.first_required_key({"properties": {"a": {}, "b": {}}}) == "a"
    assert jsonx.first_required_key({}) is None
    assert jsonx.first_required_key(None) is None
