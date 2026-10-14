from services.genie_one_parser import OneChatParser, parse_line, split_answer


def run(fixtures_dir, name):
    parser = OneChatParser()
    out = []
    for line in (fixtures_dir / name).read_text().splitlines():
        ev = parse_line(line)
        if ev is not None:
            out.extend(parser.feed(ev))
    return parser, out


def test_parse_line_variants():
    assert parse_line('data: {"type": "x"}') == {"type": "x"}
    assert parse_line(b'{"type": "y"}') == {"type": "y"}
    assert parse_line("") is None
    assert parse_line("data: [DONE]") is None
    assert parse_line(": keepalive") is None
    assert parse_line("data: {not json") is None


def test_first_turn_meta_answer_and_done(fixtures_dir):
    parser, out = run(fixtures_dir, "onechat_turn1.jsonl")
    assert out[0] == {"type": "meta", "conversation_id": "96e36e58f59e4aa685189425c77b0497"}
    assert parser.conversation_id == "96e36e58f59e4aa685189425c77b0497"
    assert [e["type"] for e in out].count("meta") == 1
    assert [e["type"] for e in out].count("answer") == 1
    assert out[-1] == {"type": "done"}


def test_steps_are_labeled_and_unique(fixtures_dir):
    _, out = run(fixtures_dir, "onechat_turn1.jsonl")
    steps = [e for e in out if e["type"] == "step"]
    assert len(steps) == len({s["id"] for s in steps})
    assert any(s["kind"] == "read" and s["label"] == "Reading jdub_demo.wyndham.fact_sales_occupancy" for s in steps)
    assert any(s["kind"] == "search" and s["label"].startswith("Searching assets") for s in steps)
    sql_steps = [s for s in steps if s["kind"] == "sql"]
    assert sql_steps and all(s["detail"] for s in sql_steps)


def test_step_results_skip_in_progress(fixtures_dir):
    _, out = run(fixtures_dir, "onechat_turn1.jsonl")
    summaries = [e["summary"] for e in out if e["type"] == "step_result"]
    assert "Found 11 results" in summaries
    assert not any("in_progress" in s for s in summaries)


def test_query_event_typed_columns_and_count(fixtures_dir):
    _, out = run(fixtures_dir, "onechat_turn1.jsonl")
    q = next(e for e in out if e["type"] == "query" and e["id"] == "query_801e01")
    assert [c["name"] for c in q["columns"]] == ["brand", "total_room_revenue"]
    assert q["total_row_count"] == 20 and len(q["rows"]) == 20
    assert "fact_sales_occupancy" in q["sql"]


def test_answer_segments_reference_embedded_query(fixtures_dir):
    _, out = run(fixtures_dir, "onechat_turn1.jsonl")
    segments = next(e for e in out if e["type"] == "answer")["segments"]
    assert segments[0]["type"] == "markdown"
    assert any(s["type"] == "query" and s["id"] == "query_801e01" for s in segments)


def test_followup_turn(fixtures_dir):
    parser, out = run(fixtures_dir, "onechat_followup.jsonl")
    assert parser.conversation_id == "cbca2fa1aec147729354d8be0e35eb67"
    assert [e["type"] for e in out].count("answer") == 1
    assert [e["type"] for e in out].count("query") == 1


def test_split_answer_plain_text():
    assert split_answer("Just text") == [{"type": "markdown", "text": "Just text"}]


def test_split_answer_keeps_embedded_markdown():
    text = "Intro\n\n<!-- begin-embedded:query_abc -->\n| a |\n| --- |\n| 1 |\n<!-- end-embedded:query_abc -->\n\nOutro"
    assert split_answer(text) == [
        {"type": "markdown", "text": "Intro"},
        {"type": "query", "id": "query_abc", "markdown": "| a |\n| --- |\n| 1 |"},
        {"type": "markdown", "text": "Outro"},
    ]


def test_unknown_event_and_duplicate_message():
    p = OneChatParser()
    assert p.feed({"type": "response.something_new"}) == []
    msg = {"type": "response.output_item.added", "item": {"type": "message", "id": "m1", "content": [{"type": "output_text", "text": "  hmm  "}], "metadata": {"ui_type": "THOUGHT"}}}
    assert p.feed(msg) == [{"type": "thinking", "text": "hmm"}]
    assert p.feed(msg) == []


def test_failed_done_emits_error_then_done():
    out = OneChatParser().feed({"type": "response.done", "response": {"status": "failed"}})
    assert out[0]["type"] == "error" and out[0]["kind"] == "upstream"
    assert out[-1] == {"type": "done"}


def test_bad_total_row_count_is_zero():
    p = OneChatParser()
    out = p.feed({"type": "response.output_item.done", "item": {"type": "function_call_output", "call_id": "c1", "status": "completed", "output": "Query returned 1 rows:", "metadata": {"embed_id": "query_x", "result_data": {"columns": [{"name": "n", "type_text": "INT"}], "preview_rows": [["1"]], "total_row_count": "lots"}}}})
    q = next(e for e in out if e["type"] == "query")
    assert q["total_row_count"] == 0 and q["sql"] is None


def test_malformed_items_never_raise():
    p = OneChatParser()
    for ev in [{"type": "response.output_item.added"}, {"type": "response.output_item.added", "item": None},
               {"type": "response.output_item.added", "item": {"type": "function_call", "arguments": "{bad"}},
               {"type": "response.output_item.added", "item": {"type": "message", "content": "not a list"}}]:
        assert p.feed(ev) == []


def test_columns_without_name_dropped():
    p = OneChatParser()
    out = p.feed({"type": "response.output_item.done", "item": {"type": "function_call_output", "call_id": "c1", "output": "Query returned 1 rows:", "metadata": {"embed_id": "query_x", "result_data": {"columns": [{"type_text": "INT"}, {"name": "n", "type_text": "INT"}], "preview_rows": [["1"]], "total_row_count": 1}}}})
    q = next(e for e in out if e["type"] == "query")
    assert q["columns"] == [{"name": "n", "type": "INT"}]


def test_step_result_dropped_without_call_id():
    p = OneChatParser()
    out = p.feed({"type": "response.output_item.done", "item": {"type": "function_call_output", "output": "Query returned 1 rows:", "metadata": {}}})
    assert out == []
