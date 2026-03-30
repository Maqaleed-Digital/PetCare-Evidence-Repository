from FND.CODE_SCAFFOLD.audit_prod_append_only import ZERO64, make_record, append_record, to_jsonl
from FND.CODE_SCAFFOLD.audit_hash_chain_verify import parse_jsonl, verify_chain

def build_ledger():
    ledger = []
    r1 = make_record(1,"t1","u1","admin","event.a",{"x":1},ZERO64,"20260101T000000Z")
    ledger = append_record(ledger, r1)
    r2 = make_record(2,"t1","u1","admin","event.b",{"y":2},ledger[-1].record_hash,"20260101T000001Z")
    ledger = append_record(ledger, r2)
    r3 = make_record(3,"t1","u1","admin","event.c",{"z":3},ledger[-1].record_hash,"20260101T000002Z")
    ledger = append_record(ledger, r3)
    return ledger

def test_verify_pass():
    s = to_jsonl(build_ledger())
    ok, msg = verify_chain(parse_jsonl(s))
    assert ok is True
    assert msg == "PASS"

def test_tamper_payload_fails():
    s = to_jsonl(build_ledger())
    recs = parse_jsonl(s)
    recs[2]["payload"]["z"] = 999
    ok, msg = verify_chain(recs)
    assert ok is False
    assert "RECORD_HASH_MISMATCH" in msg

def test_tamper_prev_hash_fails():
    s = to_jsonl(build_ledger())
    recs = parse_jsonl(s)
    recs[1]["prev_hash"] = "1"*64
    ok, msg = verify_chain(recs)
    assert ok is False
