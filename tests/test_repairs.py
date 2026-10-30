"""Regression counterexamples use invented SYNTH evidence exclusively."""
import copy
import json
import unittest
from unittest.mock import patch
from credentialing.validation import GroundworkError
from credentialing.writer import SnapshotWriter
from tests.test_workflow import WorkflowTests
from tools.synthetic_workflow import initial,decision_document,record


class RepairTests(WorkflowTests):
    def test_later_matching_reply_does_not_replace_applicant_resolution(self):
        state=self.start();one,_=self.run_batch(state);rows,_=initial()
        bad=dict(rows['verification-replies.csv'][-1],reply_id='SYNTH-CONFLICT',received_date='2026-04-01',verified_from='2003-08-01')
        two=self.stage(2,{'verification-replies.csv':[bad]},previous=state);second,_=self.run_batch(two,one['workflow_sha256'])
        good=dict(rows['verification-replies.csv'][-1],reply_id='SYNTH-LATER',received_date='2026-05-01')
        three=self.stage(3,{'verification-replies.csv':[good]},previous=two);result,_=self.run_batch(three,second['workflow_sha256'])
        case=self.result(result)['applications'][0]
        self.assertEqual(case['elements']['experience']['state'],'discrepancy')
        self.assertFalse(case['packet']['presentable'])

    def test_old_reply_does_not_satisfy_amended_entry_request(self):
        state=self.start();one,_=self.run_batch(state);base,_=initial()
        rows={name:copy.deepcopy(base[name]) for name in ('applications.csv','declared-history.csv','application-disclosures.csv','declared-credentials.csv','privilege-requests.csv')}
        for values in rows.values():
            for row in values:row['revision']='2'
        rows['applications.csv'][0]['received_date']='2026-03-30'
        rows['declared-history.csv'][-1]['contact_name']='SYNTH changed contact'
        rows['verification-attempts.csv']=[record('verification-attempts.csv',attempt_id='SYNTH-AMENDED-REQUEST',application_id='SYNTH-WORKFLOW',element='affiliation-and-employment',subject_ref='SYNTH-E2',attempt_date='2026-03-31',attempted_with='SYNTH changed contact',method='portal',outcome='request sent')]
        two=self.stage(2,rows,previous=state);result,_=self.run_batch(two,one['workflow_sha256']);case=self.result(result)['applications'][0]
        request=next(r for r in case['requests'] if r['subject_ref']=='SYNTH-E2')
        self.assertFalse(request['reply_qualifies']);self.assertFalse(request['request_satisfied'])
        self.assertTrue(any('SYNTH-E2' in q['item'] and q['due']=='2026-04-21' for q in case['action_queue']))

    def test_requested_unavailable_policy_remains_review_work(self):
        def change(rows,docs):
            for r in rows['privilege-requests.csv']:r['criteria_version_cited']='SYNTH-UNKNOWN'
        state=self.start(change);result,_=self.run_batch(state);case=self.result(result)['applications'][0]
        self.assertIsNone(case['packet']['presentable'])
        self.assertEqual(case['elements']['certification']['state'],'outstanding')
        self.assertTrue(all(g['supported'] is None for g in case['elements']['certification']['detail']['groups']))

    def test_partial_source_reply_does_not_satisfy_whole_request(self):
        def change(rows,docs):
            rows['verification-replies.csv'][0].update(outcome='partial',verified_to='')
            rows['verification-attempts.csv'].append(record('verification-attempts.csv',attempt_id='SYNTH-PARTIAL',application_id='SYNTH-WORKFLOW',element='education-and-training',subject_ref='SYNTH-E0',attempt_date='2026-01-02',method='portal',outcome='request sent'))
        state=self.start(change);result,_=self.run_batch(state);case=self.result(result)['applications'][0]
        request=next(r for r in case['requests'] if r['subject_ref']=='SYNTH-E0')
        self.assertTrue(request['reply_observed']);self.assertFalse(request['request_satisfied'])
        self.assertTrue(any('SYNTH-E0' in q['item'] and q['due']=='2026-01-23' for q in case['action_queue']))

    def test_later_reply_with_unknown_accreditation_does_not_close_prior_question(self):
        def change(rows,docs):
            docs.pop('letters/SYNTH-review.md')
            rows['verification-replies.csv']=[r for r in rows['verification-replies.csv'] if r['entry_id']!='SYNTH-E1']
        state=self.start(change);one,_=self.run_batch(state);rows,_=initial()
        two=self.stage(2,{'verification-replies.csv':[dict(rows['verification-replies.csv'][1],received_date='2026-04-01')]},previous=state)
        result,_=self.run_batch(two,one['workflow_sha256']);case=self.result(result)['applications'][0]
        self.assertTrue(case['elements']['certification']['detail']['eligibility_question_pending'])
        self.assertTrue(any(q['owner']=='Clinical Director' and 'eligibility' in q['item'] for q in case['action_queue']))
        self.assertIsNone(case['packet']['presentable'])

    def test_later_contradictory_source_reopens_matching_entry(self):
        state=self.start();one,_=self.run_batch(state)
        rows,_=initial();reply=copy.deepcopy(rows['verification-replies.csv'][-1])
        reply.update(reply_id='SYNTH-CORRECTION',received_date='2026-04-01',verified_from='2003-08-01',outcome='confirmed-with-discrepancy')
        two=self.stage(2,{'verification-replies.csv':[reply]},previous=state)
        result,_=self.run_batch(two,one['workflow_sha256']);case=self.result(result)['applications'][0]
        self.assertEqual(case['elements']['experience']['state'],'discrepancy')
        self.assertFalse(case['packet']['presentable'])
        self.assertEqual(len(case['elements']['experience']['detail']['entries'][0]['replies']),2)
        self.assertEqual(case['elements']['education']['state'],'resolved')

    def test_unavailable_cited_policy_cannot_admit_or_activate(self):
        state=self.start();one,_=self.run_batch(state)
        two=self.stage(2,docs={'decisions/SYNTH-version.md':decision_document(outcome='approved',**{'Criteria version':'SYNTH-UNAVAILABLE'})},previous=state)
        result,_=self.run_batch(two,one['workflow_sha256']);case=self.result(result)['applications'][0]
        self.assertIsNone(case['decisions'][0]['result']['admitted'])
        self.assertIsNone(case['activation']);self.assertIsNone(case['approval_decision_id'])
        self.assertTrue(any('criteria version' in q['item'] for q in case['action_queue']))

    def test_inadmissible_material_does_not_answer_source_request(self):
        def change(rows,docs):
            rows['verification-replies.csv'][0]['received_from']='Applicant — copy of diploma'
            rows['verification-attempts.csv'].append(record('verification-attempts.csv',attempt_id='SYNTH-REG',application_id='SYNTH-WORKFLOW',element='education-and-training',subject_ref='SYNTH-E0',attempted_with='Registrar',attempt_date='2026-01-02',method='portal',outcome='request sent'))
        state=self.start(change);result,_=self.run_batch(state);case=self.result(result)['applications'][0]
        req=next(r for r in case['requests'] if r['subject_ref']=='SYNTH-E0')
        self.assertTrue(req['reply_observed']);self.assertFalse(req['reply_qualifies']);self.assertFalse(req['request_satisfied'])
        self.assertTrue(any('SYNTH-E0' in q['item'] and q['due']=='2026-01-23' for q in case['action_queue']))

    def test_no_verified_training_routes_temporary_question(self):
        def change(rows,docs):rows['verification-replies.csv']=[r for r in rows['verification-replies.csv'] if r['entry_id']!='SYNTH-E1']
        state=self.start(change);result,_=self.run_batch(state);case=self.result(result)['applications'][0]
        self.assertTrue(any(q['owner']=='Clinical Director' and 'eligibility' in q['item'] for q in case['action_queue']))
        self.assertNotEqual(case['status'],'discontinued')
        rows,_=initial();two=self.stage(2,{'verification-replies.csv':[dict(rows['verification-replies.csv'][1],received_date='2026-04-01')]},previous=state)
        result,_=self.run_batch(two,result['workflow_sha256']);case=self.result(result)['applications'][0]
        self.assertFalse(any(q['owner']=='Clinical Director' and 'eligibility' in q['item'] for q in case['action_queue']))

    def test_owed_element_review_uses_outstanding_without_claiming_pass(self):
        def change(rows,docs):docs.pop('letters/SYNTH-review.md')
        state=self.start(change);result,_=self.run_batch(state);case=self.result(result)['applications'][0]
        self.assertEqual(case['elements']['certification']['state'],'outstanding')
        self.assertIsNone(case['elements']['certification']['nothing_owed'])
        self.assertIsNone(case['packet']['presentable'])

    def test_failure_receipt_never_selects_old_success_as_latest_attempt(self):
        state=self.start();one,_=self.run_batch(state)
        index=self.root/'deliverables/workflow/current.json';before=index.read_bytes()
        with self.assertRaises(GroundworkError):self.run_batch('0'*64)
        latest=json.loads((self.root/'deliverables/workflow/latest-attempt.json').read_text())
        self.assertEqual(latest['result'],'failed');self.assertEqual(index.read_bytes(),before)
        self.assertEqual(latest['affected_scope']['requested_state'],'0'*64)
        result,_=self.run_batch(state)
        self.assertEqual(result['workflow_sha256'],one['workflow_sha256'])
        self.assertEqual(json.loads((self.root/'deliverables/workflow/latest-attempt.json').read_text())['result'],'consumed')

    def test_failure_receipt_survives_snapshot_rollback_and_is_logged_on_retry(self):
        state=self.start();one,_=self.run_batch(state);two=self.stage(2,previous=state)
        with patch.object(SnapshotWriter,'publish',side_effect=OSError('SYNTHETIC disk failure')):
            with self.assertRaises(OSError):self.run_batch(two,one['workflow_sha256'])
        latest=json.loads((self.root/'deliverables/workflow/latest-attempt.json').read_text())
        self.assertEqual(latest['result'],'failed');self.assertEqual(latest['error'],'filesystem_error')
        self.assertEqual(latest['batch'],2);self.assertIn('retained_workflow_sha256',latest)
        result,code=self.run_batch(two,one['workflow_sha256']);self.assertEqual(code,0)
        self.assertIn(latest['attempt_id'],(self.root/'deliverables/run-log.md').read_text())


def load_tests(loader, tests, pattern):
    # Inherit fixture helpers without re-counting every baseline test twice.
    return unittest.TestSuite(RepairTests(name) for name in RepairTests.__dict__ if name.startswith('test_'))
