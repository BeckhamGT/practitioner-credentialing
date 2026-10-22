"""Business-path tests with expressly invented evidence, no actual-case overrides."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from credentialing.human_review import observations
from credentialing.processor import process_run
from credentialing.storage import Store
from credentialing.validation import GroundworkError,digest,json_bytes,load_batch
from credentialing.workflow import (all_known,entry_checks,evaluate,process,role_equivalent,visible)
from credentialing.workflow_store import WorkflowStore
from credentialing.elements import load_element_rules
from credentialing.review import read_rows,latest_applications
from credentialing.snapshots import verify_snapshot
from tools.synthetic_workflow import APP,CLOCKS,decision_document,initial,make_batch,record

ROOT=Path(__file__).resolve().parents[1];RULES=ROOT/'references/element-rules.json';SHA=digest(RULES.read_bytes());SCHEMA=ROOT/'snapshot.schema.json'


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
        (self.root/'deliverables').mkdir();(self.root/'deliverables/rules.md').write_text('SYNTHETIC ONLY rules fixture; published policy pins in repository')
        self.store=Store(self.root/'evidence');self.work=self.root/'workflow'

    def stage(self,batch,rows=None,docs=None,previous=None):
        p=make_batch(self.root/f'input-{batch}',batch,rows,docs);manifest,raw,contents,_=load_batch(p,batch)
        return self.store.stage(manifest,raw,contents,previous)['state_sha256']

    def run_batch(self,state,previous=None):
        return process_run(self.store.root,state,self.work,previous,RULES,SHA,self.root,SCHEMA)

    def result(self,receipt):return WorkflowStore(self.work).at(receipt['workflow_sha256'])

    def start(self,modify=None):
        rows,docs=initial()
        if modify:modify(rows,docs)
        return self.stage(1,rows,docs)

    def test_three_batches_full_projection_exact_grant_future_start_conditions_and_rerun(self):
        a=self.start();one,code=self.run_batch(a);self.assertEqual(code,0)
        case=self.result(one)['applications'][0];self.assertEqual(case['status'],'packet-presentable');self.assertTrue(case['packet']['presentable'])
        b=self.stage(2,docs={'decisions/SYNTH-GB.md':decision_document()},previous=a);two,code=self.run_batch(b,one['workflow_sha256']);self.assertEqual(code,0)
        case=self.result(two)['applications'][0];self.assertEqual(case['status'],'approved-not-yet-effective');self.assertFalse(case['activation']['active_at_export']);self.assertEqual(case['activation']['privileges'],['PRIV-FM']);self.assertEqual(case['activation']['cycle_end'],'2027-04-24')
        self.assertEqual({c['due'] for c in case['monitored_conditions']},{'2026-04-30','2026-12-31'})
        doc=f'# SYNTHETIC satisfaction\n\n**Date:** 2026-05-02\n**Application:** {APP}\n**Recorded by:** Ms. Renata Kowalczyk, CPMSM\n**Condition satisfied:** SYNTH named monitoring evidence\n'
        c=self.stage(3,docs={'letters/SYNTH-satisfaction.md':doc},previous=b);three,code=self.run_batch(c,two['workflow_sha256']);self.assertEqual(code,0)
        case=self.result(three)['applications'][0];self.assertEqual(case['status'],'active-with-conditions');self.assertTrue(case['activation']['active_at_export'])
        named=next(x for x in case['monitored_conditions'] if x['condition']=='SYNTH named monitoring evidence');self.assertTrue(named['satisfied']);self.assertEqual([x['event'] for x in named['events']],['became-finding','satisfied-by-naming-record'])
        raw=(self.root/'deliverables/snapshots/batch-03.json').read_bytes();repeat,code=self.run_batch(c,two['workflow_sha256']);self.assertEqual(code,0);self.assertEqual(repeat['workflow_result'],'unchanged');self.assertEqual(raw,(self.root/'deliverables/snapshots/batch-03.json').read_bytes())
        self.assertEqual(len(verify_snapshot(self.root,'deliverables/snapshots/batch-03.json',json.loads(SCHEMA.read_text()))['checked']),3)
        self.assertTrue(any(r['operationally_closed']=='no-longer-needed' for r in case['requests']))

    def test_unknown_signature_does_not_suppress_resolved_elements_or_invent_failure(self):
        a=self.start(lambda r,d:d.pop('letters/SYNTH-review.md'));one,code=self.run_batch(a);self.assertEqual(code,3);case=self.result(one)['applications'][0]
        self.assertEqual(case['elements']['licensure']['state'],'resolved');self.assertEqual(case['elements']['references']['detail']['qualifying_distinct_referees'],2)
        self.assertIsNone(case['intake']['complete']);self.assertIsNone(case['packet']['presentable']);self.assertIsNone(case['status']);self.assertFalse((self.root/'deliverables/snapshots').exists());self.assertEqual({q['dependency'] for q in case['action_queue'] if q['dependency'] in ('G1','G2')},{'G1','G2'})

    def test_known_false_packet_condition_is_independent_of_unknown_signature(self):
        def change(rows,docs):docs.pop('letters/SYNTH-review.md');rows['peer-reference-replies.csv'].pop()
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0]
        self.assertFalse(case['packet']['presentable']);self.assertIn('references',case['packet']['established_negative_dependencies']);self.assertIn('intake_complete',case['packet']['unknown_dependencies'])

    def test_roles_are_format_labels_not_false_discrepancies_or_aliases(self):
        self.assertTrue(role_equivalent('Staff Physician','Employment — Staff Physician'));self.assertTrue(role_equivalent('Doctor of Medicine','Degree — Doctor of Medicine'));self.assertTrue(role_equivalent('Family Medicine Residency','Residency — Family Medicine'));self.assertFalse(role_equivalent('Surgeon','Employment — Staff Physician'))

    def test_no_later_batch_or_decision_day_reply_can_justify_earlier_admission(self):
        def change(rows,docs):rows['peer-reference-replies.csv'][1]['received_date']='2026-03-16'
        a=self.start(change);one,_=self.run_batch(a)
        b=self.stage(2,docs={'decisions/SYNTH-GB.md':decision_document(outcome='approved',stamp='2026-03-16')},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);d=self.result(two)['decision_history'][0]
        self.assertFalse(d['result']['admitted']);self.assertEqual(d['result']['reason'],'prior presentable packet')

    def test_wrong_body_refused_before_missing_packet_and_never_rewritten(self):
        a=self.start(lambda r,d:d.pop('letters/SYNTH-review.md'));one,_=self.run_batch(a)
        text=decision_document(outcome='approved',Body='Executive Committee of the Medical Staff',Signatory='Dr. Peter Vandermolen, MD',Role='Chair, Executive Committee of the Medical Staff')
        b=self.stage(2,docs={'decisions/SYNTH-wrong.md':text},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);d=self.result(two)['decision_history'][0];self.assertEqual(d['result'],{'admitted':False,'reason':'body-authority'})
        c=self.stage(3,previous=b);three,_=self.run_batch(c,two['workflow_sha256']);self.assertEqual(d,self.result(three)['decision_history'][0])

    def test_duplicate_gb_and_explicit_supersession(self):
        a=self.start();one,_=self.run_batch(a)
        b=self.stage(2,docs={'decisions/SYNTH-1.md':decision_document('SYNTH-FIRST','approved')},previous=a);two,_=self.run_batch(b,one['workflow_sha256'])
        c=self.stage(3,docs={'decisions/SYNTH-2.md':decision_document('SYNTH-SECOND','approved',stamp='2026-05-01')},previous=b);three,_=self.run_batch(c,two['workflow_sha256']);self.assertEqual(self.result(three)['decision_history'][-1]['result'],{'admitted':False,'reason':'supersession'})

    def test_admitted_deferral_is_business_hold_and_denial_is_not_activation(self):
        a=self.start();one,_=self.run_batch(a)
        b=self.stage(2,docs={'decisions/SYNTH-1.md':decision_document('SYNTH-HOLD','deferred-pending-information',Reason='SYNTH further outside-practice reference')},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);self.assertEqual(self.result(two)['applications'][0]['status'],'deferred')
        c=self.stage(3,docs={'decisions/SYNTH-2.md':decision_document('SYNTH-DENY','denied',stamp='2026-05-01',Reason='SYNTH human judgment',Supersedes='SYNTH-HOLD')},previous=b);three,_=self.run_batch(c,two['workflow_sha256']);case=self.result(three)['applications'][0];self.assertEqual(case['status'],'denied');self.assertIsNone(case['activation']);self.assertTrue(case['decisions'][-1]['result']['admitted'])

    def test_contact_change_reopens_only_affected_entry_and_current_reply_recovers(self):
        a=self.start();one,_=self.run_batch(a);base,docs=initial();revision=copy.deepcopy(base['applications.csv']);revision[0].update(revision='2',received_date='2026-03-30');history=copy.deepcopy(base['declared-history.csv'])
        for row in history:row['revision']='2'
        history[-1]['contact_name']='SYNTH New supervisor'
        rows={'applications.csv':revision,'declared-history.csv':history}
        for name in ('application-disclosures.csv','declared-credentials.csv','privilege-requests.csv','peer-referees.csv'):
            rows[name]=copy.deepcopy(base[name])
            for row in rows[name]:row['revision']='2'
        b=self.stage(2,rows,previous=a);two,_=self.run_batch(b,one['workflow_sha256']);case=self.result(two)['applications'][0];self.assertEqual(case['elements']['experience']['state'],'discrepancy');self.assertEqual(case['elements']['education']['state'],'resolved');self.assertIsNone(case['intake']['CV_reconciled'])
        reply=copy.deepcopy(base['verification-replies.csv'][-1]);reply.update(reply_id='SYNTH-REVERIFY',received_date='2026-05-01')
        c=self.stage(3,{'verification-replies.csv':[reply]},previous=b);three,_=self.run_batch(c,two['workflow_sha256']);case=self.result(three)['applications'][0];self.assertEqual(case['elements']['experience']['state'],'resolved');self.assertTrue(any(h['value']['revision']==1 for h in case['history']))

    def test_missing_and_corrupt_workflow_predecessors_never_restart(self):
        a=self.start();one,_=self.run_batch(a);b=self.stage(2,previous=a)
        with self.assertRaises(GroundworkError):self.run_batch(b,None)
        path=self.work/'objects'/f"{one['workflow_sha256']}.json";original=path.read_bytes();path.write_bytes(original+b' ')
        with self.assertRaises(GroundworkError):self.run_batch(b,one['workflow_sha256'])
        path.write_bytes(original);two,_=self.run_batch(b,one['workflow_sha256']);self.assertEqual(two['batch'],2)

    def test_unknown_conjunction_preserves_known_negative(self):
        self.assertFalse(all_known([None,False]));self.assertIsNone(all_known([None,True]));self.assertTrue(all_known([True,True]))

    def test_unknown_decision_prerequisite_remains_unknown_not_refusal(self):
        a=self.start(lambda r,d:d.pop('letters/SYNTH-review.md'));one,_=self.run_batch(a)
        b=self.stage(2,docs={'decisions/SYNTH.md':decision_document(outcome='approved')},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);result=self.result(two)['decision_history'][0]['result'];self.assertIsNone(result['admitted']);self.assertIn('presentability',result['reason'])

    def test_msp_review_cannot_grant_or_reference_unknown_evidence(self):
        rows,docs=initial();docs['letters/SYNTH-review.md']=docs['letters/SYNTH-review.md'].replace('"application_signature": true','"grant_privileges": true');a=self.stage(1,rows,docs)
        with self.assertRaises(GroundworkError):self.run_batch(a)
        self.assertFalse((self.work/'HEAD.json').exists())

    def test_unknown_or_applicant_carried_source_stays_outstanding(self):
        def change(rows,docs):rows['verification-replies.csv'][0]['received_from']='Applicant — personally delivered'
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertEqual(case['elements']['education']['state'],'outstanding');self.assertFalse(case['packet']['presentable'])

    def test_wrong_condition_name_does_not_satisfy_owed_condition(self):
        a=self.start();one,_=self.run_batch(a);b=self.stage(2,docs={'decisions/SYNTH.md':decision_document()},previous=a);two,_=self.run_batch(b,one['workflow_sha256'])
        doc=f'# SYNTHETIC satisfaction\n\n**Date:** 2026-04-25\n**Application:** {APP}\n**Recorded by:** Ms. Renata Kowalczyk, CPMSM\n**Condition satisfied:** a different condition\n'
        c=self.stage(3,docs={'letters/SYNTH-other.md':doc},previous=b);three,_=self.run_batch(c,two['workflow_sha256']);condition=next(c for c in self.result(three)['applications'][0]['monitored_conditions'] if c['condition']=='SYNTH named monitoring evidence');self.assertFalse(condition['satisfied']);self.assertTrue(condition['finding']);self.assertEqual(condition['owner'],'Clinical Director')

    def test_real_notice_clock_partial_reply_does_not_reset_or_become_g1_failure(self):
        rows,docs=initial();docs.pop('letters/SYNTH-review.md');rows['applications.csv'][0].update(release_signed_date='',cv_received_date='')
        docs['letters/SYNTH-missing.md']=f'# Missing items on your application\n\n**Date:** 2026-02-18\n**Application:** {APP}\n\nMissing: Authorization and Release, signed and dated; and a current curriculum vitae. Reply within 30 calendar days, that is by 2026-03-20.\n'
        a=self.stage(1,rows,docs);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertEqual(case['status'],'intake-incomplete');self.assertFalse(case['intake']['verification_request_permitted'])
        revised={}
        for name in ('applications.csv','declared-history.csv','declared-credentials.csv','privilege-requests.csv','application-disclosures.csv','peer-referees.csv'):
            revised[name]=copy.deepcopy(rows[name])
            for row in revised[name]:row['revision']='2'
        revised['applications.csv'][0].update(received_date='2026-03-18',release_signed_date='2026-03-18')
        b=self.stage(2,revised,previous=a);two,_=self.run_batch(b,one['workflow_sha256']);case=self.result(two)['applications'][0]
        self.assertEqual(case['status'],'ineligible-clock-expired');self.assertEqual(case['intake']['clocks'][0]['due'],'2026-03-20');self.assertTrue(case['intake']['release_permission']);self.assertFalse(case['intake']['verification_request_permitted']);self.assertIsNone(case['intake']['conditions']['1_application_signed_and_dated'])

    def test_restricted_finding_persists_after_cd_disposition_ends_hold(self):
        def change(rows,docs):
            rows['licence-lookup-wa.csv'][0]['actiontaken']='Yes';rows['application-disclosures.csv'][0].update(answer='Yes',applicant_comment='SYNTH monitoring agreement')
            docs['letters/SYNTH-board.md']=f'# SYNTHETIC board reply\n\n**Date:** 2026-03-05\n**Application:** {APP}\n**From:** Washington State Department of Health\n\nSYNTH-MD practises under supervision in a monitoring programme.\n'
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertEqual(case['elements']['licensure']['state'],'finding');self.assertFalse(case['elements']['licensure']['nothing_owed'])
        doc=f'# SYNTHETIC Licensure finding and high-risk finding\n\n**Date:** 2026-04-01\n**Application:** {APP}\n**Recorded by:** Dr. Marguerite Oyelaran, MD, Clinical Director\n\nPresent the file with the finding. Do not discontinue the application.\n'
        b=self.stage(2,docs={'dispositions/SYNTH-cd.md':doc},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);case=self.result(two)['applications'][0];self.assertEqual(case['elements']['licensure']['state'],'finding');self.assertTrue(case['elements']['licensure']['nothing_owed']);self.assertTrue(case['packet']['presentable'])

    def test_board_eligible_good_standing_note_and_future_end_support_published_groups(self):
        def change(rows,docs):rows['certification-replies.csv'][0].update(certification_status='Not certified',expiry_date='',notes='Candidate in good standing; board eligible through 2027-06-30.')
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertEqual(case['elements']['certification']['detail']['supported'],['PRIV-FM','PRIV-HOSP']);self.assertTrue(case['packet']['presentable'])

    def test_secondary_route_requires_msp_record_even_with_documented_impossibility(self):
        def change(rows,docs):
            reply=rows['verification-replies.csv'][0];reply.update(received_from='Medical staff office — SYNTH Practice',attester_organization='SYNTH Practice',notes='School closed; no designated source holds record; this most recent affiliation holds the original registrar verification.')
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertIsNone(case['elements']['education']['state']);self.assertIsNone(case['packet']['presentable'])

    def test_licence_renewal_retains_and_satisfies_its_exact_old_condition(self):
        def change(rows,docs):rows['licence-lookup-wa.csv'][0]['expirationdate']='2026-04-30'
        a=self.start(change);one,_=self.run_batch(a);b=self.stage(2,docs={'decisions/SYNTH.md':decision_document(outcome='approved')},previous=a);two,_=self.run_batch(b,one['workflow_sha256'])
        rows,_=initial();lookup=rows['licence-lookup-wa.csv'][0];lookup.update(expirationdate='2028-04-30',lastissuedate='2026-05-01',lookup_date='2026-05-10')
        c=self.stage(3,{'licence-lookup-wa.csv':[lookup]},previous=b);three,_=self.run_batch(c,two['workflow_sha256']);case=self.result(three)['applications'][0];old=next(c for c in case['monitored_conditions'] if c['due']=='2026-04-30');self.assertTrue(old['satisfied']);self.assertEqual(old['events'][0]['event'],'became-finding');self.assertEqual(old['events'][-1]['date'],'2026-05-10');self.assertEqual(case['status'],'active')

    def test_full_pipeline_snapshot_failure_recovery_retry_keeps_workflow_and_prior_snapshot(self):
        from credentialing.writer import SnapshotWriter
        a=self.start();one,_=self.run_batch(a);before=(self.root/'deliverables/snapshots/batch-01.json').read_bytes();b=self.stage(2,previous=a);atomic=SnapshotWriter._atomic
        def fail(path,raw):
            if path==self.root/'deliverables/snapshots/batch-02.json':raise OSError('SYNTHETIC injected write failure')
            return atomic(path,raw)
        with patch.object(SnapshotWriter,'_atomic',side_effect=fail):
            with self.assertRaises(GroundworkError):self.run_batch(b,one['workflow_sha256'])
        self.assertEqual(WorkflowStore(self.work).current()[1]['batch'],2)
        with self.assertRaises(GroundworkError):verify_snapshot(self.root,'deliverables/snapshots/batch-01.json',json.loads(SCHEMA.read_text()))
        SnapshotWriter(self.root,json.loads(SCHEMA.read_text())).recover();self.assertEqual(before,(self.root/'deliverables/snapshots/batch-01.json').read_bytes());two,code=self.run_batch(b,one['workflow_sha256']);self.assertEqual(code,0);self.assertEqual(two['workflow_result'],'unchanged')

    def test_positive_secondary_route_is_supported_only_by_linked_authorized_msp_observation(self):
        def change(rows,docs):
            rows['verification-replies.csv'][0].update(received_from='Medical staff office — SYNTH Practice',attester_organization='SYNTH Practice',notes='School closed. No designated equivalent holds a record. Most recent surviving affiliation holds its original registrar verification.')
            docs['letters/SYNTH-review.md']=docs['letters/SYNTH-review.md'].replace('"facts": {','"facts": {"secondary_route_by_entry": {"SYNTH-E0": true},')
        a=self.start(change);one,code=self.run_batch(a);self.assertEqual(code,0);self.assertEqual(self.result(one)['applications'][0]['elements']['education']['state'],'resolved')

    def test_retained_employer_cvo_must_name_the_organization_it_acted_for(self):
        def change(rows,docs):rows['verification-replies.csv'][-1].update(received_from='Credentials verification organization — SYNTH CVO',attester_organization='SYNTH CVO',notes='Retained by SYNTH Practice; acting for SYNTH Practice')
        a=self.start(change);one,code=self.run_batch(a);self.assertEqual(code,0);self.assertEqual(self.result(one)['applications'][0]['elements']['experience']['state'],'resolved')

    def test_admitted_decision_freezes_peer_currency_date_without_borrowing_later_replies(self):
        def change(rows,docs):
            rows['applications.csv'][0].update(first_received_date='2024-01-01',received_date='2024-01-01')
            for row in rows['peer-reference-replies.csv']:row.update(signature_date='2024-05-05',received_date='2024-05-06')
            for row in rows['peer-referees.csv']:row['first_request_date']='2024-05-01'
            for row in rows['verification-attempts.csv']:row['attempt_date']='2024-05-01'
        a=self.start(change);one,_=self.run_batch(a);b=self.stage(2,docs={'decisions/SYNTH.md':decision_document(outcome='approved',stamp='2026-04-14')},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);c=self.stage(3,previous=b);three,_=self.run_batch(c,two['workflow_sha256']);refs=self.result(three)['applications'][0]['elements']['references'];self.assertTrue(refs['nothing_owed']);self.assertEqual(refs['detail']['currency_clock'],'2026-04-14')

    def test_no_reported_other_state_action_is_not_a_finding(self):
        def change(rows,docs):
            rows['declared-credentials.csv'].append(record('declared-credentials.csv',declaration_id='SYNTH-OR',application_id=APP,revision='1',credential_class='licence',issuer='Oregon Medical Board',jurisdiction_or_board='OR',number_declared='SYNTH-OR',declared_status='Active'))
            rows['licence-lookup-other-states.csv'].append(record('licence-lookup-other-states.csv',board_state='OR',licence_number='SYNTH-OR',status='Active',expiry_date='2028-01-01',disciplinary_action='None reported',verified_by='Oregon Medical Board online verification',lookup_date='2026-03-01'))
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertEqual(case['elements']['licensure']['state'],'resolved');self.assertTrue(case['elements']['licensure']['nothing_owed'])

    def test_incremental_referee_names_survive_revision_without_restatement(self):
        a=self.start();one,_=self.run_batch(a);rows,_=initial();updates={}
        for name in ('applications.csv','declared-history.csv','declared-credentials.csv','privilege-requests.csv','application-disclosures.csv'):
            updates[name]=copy.deepcopy(rows[name])
            for r in updates[name]:r['revision']='2'
        updates['applications.csv'][0]['received_date']='2026-03-30'
        b=self.stage(2,updates,previous=a);two,_=self.run_batch(b,one['workflow_sha256']);case=self.result(two)['applications'][0];self.assertTrue(case['intake']['conditions']['7_two_named_referees']);self.assertTrue(case['elements']['references']['nothing_owed'])

    def test_incomplete_condition_details_do_not_stop_other_work_or_invent_deadline(self):
        a=self.start();one,_=self.run_batch(a);doc=decision_document().replace('SYNTH named monitoring evidence — due 2026-04-30','SYNTH condition with no supplied deadline')
        b=self.stage(2,docs={'decisions/SYNTH.md':doc},previous=a);two,code=self.run_batch(b,one['workflow_sha256']);self.assertEqual(code,3);case=self.result(two)['applications'][0];self.assertEqual(case['approval_decision_id'],'SYNTH-GB');self.assertFalse(case['activation']['active_at_export']);self.assertTrue(case['condition_details_unresolved']);self.assertTrue(any('monitored_conditions' in x for x in case['schema_conflicts']))

    def test_leap_cycle_unknown_preserves_admitted_approval_and_other_results(self):
        a=self.start();one,_=self.run_batch(a);doc=decision_document(outcome='approved',**{'Effective date':'2028-02-29'})
        b=self.stage(2,docs={'decisions/SYNTH.md':doc},previous=a);two,code=self.run_batch(b,one['workflow_sha256']);self.assertEqual(code,3);case=self.result(two)['applications'][0];self.assertEqual(case['approval_decision_id'],'SYNTH-GB');self.assertIsNone(case['activation']);self.assertTrue(case['decisions'][0]['result']['admitted']);self.assertTrue(any(x.startswith('activation:') for x in case['schema_conflicts']))

    def test_unreconciled_narrative_is_review_unknown_not_a_proven_refusal(self):
        def change(rows,docs):docs['letters/SYNTH-narrative.md']=f'# SYNTHETIC narrative\n\n**Date:** 2026-03-01\n**Application:** {APP}\n\nI started at another employer at the beginning of June.\n'
        a=self.start(change);one,_=self.run_batch(a);case=self.result(one)['applications'][0];self.assertIsNone(case['packet']['presentable']);self.assertIsNone(case['packet']['requirements']['no_open_discrepancy']);self.assertEqual(case['elements']['experience']['state'],'resolved')
        b=self.stage(2,docs={'decisions/SYNTH.md':decision_document(outcome='approved')},previous=a);two,_=self.run_batch(b,one['workflow_sha256']);self.assertIsNone(self.result(two)['decision_history'][0]['result']['admitted'])

    def test_linked_source_correction_ends_only_its_own_review_and_keeps_both_sources(self):
        def change(rows,docs):
            original=f'# SYNTHETIC narrative\n\n**Date:** 2026-03-01\n**Application:** {APP}\n\nI started at another employer at the beginning of June.\n'
            correction=f'# SYNTHETIC applicant correction\n\n**Date:** 2026-03-03\n**Application:** {APP}\n\nThe narrative employer was a transcription error. My declared employer is correct.\n'
            docs['letters/SYNTH-original.md']=original;docs['letters/SYNTH-correction.md']=correction
            note=docs['letters/SYNTH-review.md'];block=json.loads(note.split('```json\n')[1].split('\n```')[0]);block['evidence'] += [{'path':'letters/SYNTH-original.md','sha256':digest(original.encode())},{'path':'letters/SYNTH-correction.md','sha256':digest(correction.encode())}];block['facts']['resolved_source_concerns']={digest(original.encode()):digest(correction.encode())}
            docs['letters/SYNTH-review.md']=note.split('```json\n')[0].replace('2026-02-08','2026-03-04')+'```json\n'+json.dumps(block,indent=2)+'\n```\n'
        a=self.start(change);one,code=self.run_batch(a);self.assertEqual(code,0);case=self.result(one)['applications'][0];self.assertTrue(case['packet']['presentable']);self.assertTrue(case['human_records']['anomalies'][0]['resolved_by']);self.assertTrue(any(d['source']['path']=='letters/SYNTH-original.md' for d in case['documents_read']))

    def test_partial_entry_observations_add_only_their_own_fact_and_keep_provenance(self):
        def change(rows,docs):
            content={'evidence':[{'path':'letters/SYNTH-intake-evidence.md','sha256':digest(docs['letters/SYNTH-intake-evidence.md'].encode())}],'facts':{'accreditation_by_entry':{'SYNTH-E2':True}}}
            docs['letters/SYNTH-review-partial.md']=f'# SYNTHETIC partial review\n\n**Date:** 2026-03-04\n**Application:** {APP}\n**Revision:** 1\n**Review schema:** credentialing-observations/1\n**Recorded by:** Ms. Renata Kowalczyk, CPMSM\n\n```json\n'+json.dumps(content)+'\n```\n'
        a=self.start(change);one,code=self.run_batch(a);self.assertEqual(code,0);facts=self.result(one)['applications'][0]['intake']['human_observations']['accreditation_by_entry'];self.assertEqual(set(facts['value']),{'SYNTH-E0','SYNTH-E1','SYNTH-E2'});self.assertNotEqual(facts['item_sources']['SYNTH-E0']['source']['path'],facts['item_sources']['SYNTH-E2']['source']['path'])
