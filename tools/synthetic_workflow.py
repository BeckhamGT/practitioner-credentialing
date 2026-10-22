"""Explicitly invented SYNTH-only input package for end-to-end demonstrations.

These givens never enter the supplied applicant evidence store.
"""

import csv
import io
import json
import re
from pathlib import Path

from credentialing.validation import LAYOUT, digest, json_bytes


CLOCKS = {1:"2026-03-16",2:"2026-04-20",3:"2026-05-18"}
APP = "SYNTH-WORKFLOW"


def record(name, **values):
    result = {k:"" for k in LAYOUT[name].split(",")};result.update(values);return result


def initial():
    rows = {k:[] for k in LAYOUT}
    def add(name,**kw):rows[name].append(record(name,**kw))
    add("applications.csv",application_id=APP,revision="1",applicant_id="SYNTH-P",received_date="2026-01-01",first_received_date="2026-01-01",first_name="Example",last_name="Synthetic",birth_year="1975",degree="MD",practice_state="WA",discipline="Family Medicine",release_signed_date="2026-01-01",cv_received_date="2026-01-01")
    for n in range(1,9):add("application-disclosures.csv",application_id=APP,revision="1",question_code=f"PPQ-{n}",question_text="SYNTHETIC question",answer="No")
    for code in ("PRIV-FM","PRIV-HOSP"):add("privilege-requests.csv",request_id="SYNTH-"+code,application_id=APP,revision="1",privilege_code=code,privilege_name="SYNTHETIC",criteria_version_cited="LARK-PRIV-2026.1")
    for i,(kind,org,role,start,end,label,sender,element) in enumerate([
        ("medical-school","SYNTH School","Doctor of Medicine","1996-08-20","2000-06-30","Degree — Doctor of Medicine","Registrar's office","education-and-training"),
        ("residency","SYNTH Hospital","Family Medicine Residency","2000-07-01","2003-06-30","Residency — Family Medicine","Graduate medical education office","education-and-training"),
        ("employment","SYNTH Practice","Staff Physician","2003-07-01","","Employment — Staff Physician","Medical staff office","affiliation-and-employment")]):
        add("declared-history.csv",entry_id=f"SYNTH-E{i}",application_id=APP,revision="1",entry_type=kind,organization=org,role=role,from_date=start,to_date=end,contact_name="SYNTH contact",contact_email="synthetic@example.invalid")
        add("verification-replies.csv",reply_id=f"SYNTH-V{i}",application_id=APP,entry_id=f"SYNTH-E{i}",element=element,attester_organization=org,attester_name="SYNTH source",received_from=sender+" — "+org,verified_credential=label,verified_from=start,verified_to=end,outcome="confirmed",requested_date="2026-01-02",received_date=f"2026-02-0{i+1}",reply_method="direct portal")
    add("declared-credentials.csv",declaration_id="SYNTH-L",application_id=APP,revision="1",credential_class="licence",issuer="Washington State Department of Health",jurisdiction_or_board="WA",number_declared="SYNTH-MD",declared_status="Active",declared_expiry_date="2026-12-31")
    add("declared-credentials.csv",declaration_id="SYNTH-C",application_id=APP,revision="1",credential_class="certification",issuer="American Board of Family Medicine",jurisdiction_or_board="ABFM",declared_status="Board certified")
    add("certification-replies.csv",reply_id="SYNTH-CR",application_id=APP,declaration_id="SYNTH-C",board_name="American Board of Family Medicine",board_code="ABFM",received_from="Certifying board — American Board of Family Medicine",certificate_specialty="Family Medicine",certification_status="Active",initial_certification_date="2003-07-01",expiry_date="2028-12-31",requested_date="2026-01-02",received_date="2026-02-04")
    add("licence-lookup-wa.csv",credentialnumber="SYNTH-MD",status="ACTIVE",firstissuedate="2003-07-01",lastissuedate="2025-12-01",expirationdate="2026-12-31",actiontaken="No",birthyear="1975",firstname="Example",lastname="Synthetic",lookup_date="2026-03-10")
    for n in (0,1,2):
        add("peer-referees.csv",referee_id=f"SYNTH-R{n}",application_id=APP,revision="1",referee_name="SYNTH peer",referee_specialty="Family Medicine",first_request_date="2026-01-02")
        add("verification-attempts.csv",attempt_id=f"SYNTH-A{n}",application_id=APP,element="peer-reference",subject_ref=f"SYNTH-R{n}",attempted_with="SYNTH peer",attempt_date="2026-01-02",method="portal",outcome="request sent")
        if n<2:add("peer-reference-replies.csv",reply_id=f"SYNTH-RR{n}",referee_id=f"SYNTH-R{n}",application_id=APP,signature_date="2026-02-05",received_date=f"2026-02-0{6+n}",related_or_partner="No",relationship_stated="I worked directly with the applicant.",referee_specialty_stated="Family Medicine",recommendation="Recommend without reservation",comments="SYNTHETIC comments")
    evidence = f"# SYNTHETIC invented intake documents\n\n**Date:** 2026-02-01\n**Application:** {APP}\n**Revision:** 1\n\nInvented signed application, current CV comparison, declaration attestation, and degree/training accreditation evidence. NOT supplied-applicant material.\n"
    facts = {"application_signature":True,"cv_current":True,"cv_reconciled":True,"all_credentials_declared":True,"accreditation_by_entry":{"SYNTH-E0":True,"SYNTH-E1":True}}
    review = {"evidence":[{"path":"letters/SYNTH-intake-evidence.md","sha256":digest(evidence.encode())}],"facts":facts}
    note = f"# SYNTHETIC MSP observations\n\n**Date:** 2026-02-08\n**Application:** {APP}\n**Revision:** 1\n**Review schema:** credentialing-observations/1\n**Recorded by:** Ms. Renata Kowalczyk, CPMSM\n\n```json\n{json.dumps(review,indent=2)}\n```\n"
    return rows,{"letters/SYNTH-intake-evidence.md":evidence,"letters/SYNTH-review.md":note}


def decision_document(identifier="SYNTH-GB",outcome="approved-with-conditions",stamp="2026-03-20",**changes):
    fields={"Decision ID":identifier,"Body":"Governing Body","Signatory":"Ms. Corinne Batiste","Role":"Chair, Governing Body","Application":APP,"Revision":"1","Decision date":stamp,"Outcome":outcome,"Privileges":"PRIV-FM","Criteria version":"LARK-PRIV-2026.1","Reason":"SYNTHETIC conditional grant" if outcome=="approved-with-conditions" else "","Effective date":"2026-04-25","Supersedes":""};fields.update(changes)
    text="# SYNTHETIC invented decision\n\n"+"\n".join(f"**{k}:** {v}" for k,v in fields.items())+"\n"
    if outcome=="approved-with-conditions":text+="**Conditions:**\n- SYNTH named monitoring evidence — due 2026-04-30\n"
    return text


def make_batch(root,batch,rows=None,documents=None):
    root=Path(root);root.mkdir(parents=True);rows=rows or {};documents=documents or {};clock=CLOCKS[batch]
    correspondence=list(rows.get("correspondence.csv",[]))
    for i,(path,text) in enumerate(documents.items()):
        fields=dict(re.findall(r"^\*\*([^*\n]+):\*\*\s*([^\n]*)",text,re.M))
        correspondence.append(record("correspondence.csv",letter_id=f"SYNTH-DOC-{batch}-{i}",date=fields.get("Date",fields.get("Decision date")),direction="inbound",application_id=APP,correspondent="SYNTH fixture",subject="SYNTHETIC source",document_path=path))
        target=root/path;target.parent.mkdir(exist_ok=True);target.write_text(text)
    for name in LAYOUT:
        stream=io.StringIO(newline="");writer=csv.DictWriter(stream,fieldnames=LAYOUT[name].split(","),lineterminator="\n");writer.writeheader();writer.writerows(correspondence if name=="correspondence.csv" else rows.get(name,[]));(root/name).write_text(stream.getvalue())
    (root/"README.md").write_text(f"# Batch {batch} export — SYNTHETIC ONLY\n\n**Export date: {clock}**\n")
    paths=list(LAYOUT)+["README.md"]+list(documents)
    manifest={"format":"credentialing-input-manifest/1","batch":batch,"as_of":clock,"files":[{"path":name,"sha256":digest((root/name).read_bytes()),"source_id":f"SYNTH-{batch}-{i}","source_url":f"https://example.invalid/synthetic/{batch}/{i}","source_batch":batch,"kind":"records" if name.endswith('.csv') else "batch-readme" if name=="README.md" else "document"} for i,name in enumerate(paths)]}
    (root/"input.manifest.json").write_bytes(json_bytes(manifest));return root
