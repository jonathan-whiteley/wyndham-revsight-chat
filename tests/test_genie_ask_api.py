def test_blank_question_rejected(client):
    r = client.post("/api/genie/ask", json={"model": "anything", "question": "   "})
    assert r.status_code == 400
