# E-Visa Portal Knowledge Base

## 1) Purpose and Scope

This knowledge base supports the in-app E-Visa Assistant chatbot.

The assistant should answer questions about:
- How the E-Visa Portal works
- Application steps and statuses
- Visa type requirements
- Document, payment, interview, review, and issuance flow
- Role-based actions (Applicant, Officer, Supervisor, Admin)

The assistant should **not** invent case-specific outcomes, timelines, or legal advice not present in this knowledge base.

---

## 2) Assistant Behavior Guidelines (RAG Grounding Policy)

Use these rules for safe, high-quality responses:

1. Answer using only the information in this knowledge base context.
2. If the answer is missing from context, say:  
   "I do not have enough information in the current knowledge base."
3. Do not fabricate processing times, approval guarantees, or external policy details.
4. Do not claim access to hidden/internal data not explicitly provided by the user.
5. For case-specific questions ("What is my current status?"), guide users to the **Application Status** page in the portal.
6. Keep responses clear, practical, and concise.
7. If user asks for a step-by-step action, provide ordered steps.
8. If user asks which visa type to choose, provide suggestions based on purpose keywords and remind user final selection is theirs.

---

## 3) User Roles and Access

### Applicant
- Create new application
- Upload documents
- Submit application
- View application status and timeline
- View recommendations
- Pay application fee (when application is approved)
- View interview details (if interview required)
- Download issued visa PDF
- Re-apply from a rejected application

### Officer
- View review queue
- Review applications
- Approve, reject, or request more info
- Schedule/cancel/complete interviews
- Issue visa (subject to generation prerequisites)
- View personal decision history

### Supervisor
- All officer review actions
- Supervisor override panel
- View active under-review cases and recent rejections
- View audit logs and reports

### Admin
- Manage visa types (create/activate/deactivate)
- View reports
- View audit logs

---

## 4) Applicant Journey (End-to-End)

1. Create application in **Draft**.
2. Upload required documents.
3. Submit application.
4. System runs pre-screening and moves eligible applications to **Under Review**.
5. Officer/Supervisor decides:
   - Approve
   - Reject
   - Request additional information
6. If approved, applicant can pay.
7. Once payment is confirmed, visa is issued.
8. Applicant downloads visa from portal.

---

## 5) Application Statuses and Transitions

### Statuses
- DRAFT
- SUBMITTED
- PRE_SCREENING
- UNDER_REVIEW
- PENDING_INFO
- APPROVED
- REJECTED
- ISSUED
- WITHDRAWN

### Allowed transitions
- DRAFT -> SUBMITTED
- SUBMITTED -> PRE_SCREENING
- PRE_SCREENING -> UNDER_REVIEW
- UNDER_REVIEW -> APPROVED | REJECTED | PENDING_INFO
- PENDING_INFO -> UNDER_REVIEW
- APPROVED -> ISSUED

Notes:
- REJECTED and ISSUED are terminal states in current transition map.
- PENDING_INFO means applicant must provide additional details/documents before further review.

---

## 6) Visa Types (Current Rules Configuration)

Current rule-engine visa codes:
- TOURIST
- BUSINESS
- STUDENT
- NONIMMIGRANT
- TRANSIT
- MEDICAL
- CONFERENCE
- FAMILY_VISIT
- WORK

Important:
- The applicant form shows only **active** visa types from database.
- Rules are keyed by visa code.
- If a visa code exists in DB but not in rules, default required documents logic applies.

---

## 7) Required Documents by Visa Type

### TOURIST (Tourist Visa)
- PASSPORT
- PHOTO
- BANK_STATEMENT
- TRAVEL_ITINERARY

Minimum days before entry: 7

### BUSINESS (Business Visa)
- PASSPORT
- PHOTO
- INVITATION_LETTER
- BANK_STATEMENT

Minimum days before entry: 14

### STUDENT (Student Visa)
- PASSPORT
- PHOTO
- BANK_STATEMENT
- INVITATION_LETTER
- ACCOMMODATION_PROOF

Minimum days before entry: 30

### NONIMMIGRANT (Nonimmigrant Visa)
- PASSPORT
- PHOTO
- BANK_STATEMENT

Minimum days before entry: 7

### TRANSIT (Transit Visa)
- PASSPORT
- PHOTO
- TRAVEL_ITINERARY

Minimum days before entry: 3

### MEDICAL (Medical Visa)
- PASSPORT
- PHOTO
- BANK_STATEMENT
- INVITATION_LETTER
- ACCOMMODATION_PROOF

Minimum days before entry: 10

### CONFERENCE (Conference Visa)
- PASSPORT
- PHOTO
- INVITATION_LETTER
- TRAVEL_ITINERARY
- BANK_STATEMENT

Minimum days before entry: 10

### FAMILY_VISIT (Family Visit Visa)
- PASSPORT
- PHOTO
- INVITATION_LETTER
- ACCOMMODATION_PROOF
- BANK_STATEMENT

Minimum days before entry: 7

### WORK (Work Visa)
- PASSPORT
- PHOTO
- INVITATION_LETTER
- BANK_STATEMENT
- ACCOMMODATION_PROOF

Minimum days before entry: 21

### Global default required documents
- PASSPORT
- PHOTO

---

## 8) Supported Document Types

- PASSPORT
- PHOTO
- BANK_STATEMENT
- INVITATION_LETTER
- TRAVEL_ITINERARY
- ACCOMMODATION_PROOF
- OTHER

Upload form guidance:
- Accepted formats: PDF, JPG, JPEG, PNG
- Max size shown in UI: 5 MB

---

## 9) Validation and Pre-Screening Rules

### Submission-level checks (before moving from Draft)
- Passport number required
- Passport expiry required and must be in the future
- Visa type must be selected
- At least one supporting document must exist

### Rule engine checks
- Nationality global block list
- Nationality block per visa type
- Eligible nationality allowlist (if configured)
- Required document presence
- Intended entry date minimum lead time

### Hard vs soft outcomes
- Nationality failures are hard blockers in pre-screening.
- Missing documents and near entry dates can be surfaced as warnings during pre-screening.

---

## 10) Payment Flow

- Payment record is created on submission with amount = selected visa type fee.
- Payment starts as PENDING.
- Applicant can pay when status is APPROVED.
- Current UI uses **simulated payment confirmation**.
- On successful payment confirmation, application is moved to issuance path.
- Duplicate payment confirmation is prevented.

Payment statuses in system:
- PENDING
- PAID
- FAILED
- REFUNDED

---

## 11) Review Flow (Officer/Supervisor)

When application is UNDER_REVIEW:
- Approve: moves to APPROVED
- Reject: moves to REJECTED (reason required)
- Request more info: moves to PENDING_INFO

Decision records are stored with:
- Reviewer
- Decision type (APPROVED / REJECTED / REQUEST_INFO)
- Reason
- Timestamp

Decision history:
- Officer sees own decisions
- Supervisor sees all recent decisions

---

## 12) Interview Flow

Officers/Supervisors can:
- Schedule interview
- Mark interview completed
- Cancel scheduled interview

When interview is scheduled:
- `requires_interview = True`

When interview is completed:
- `interview_completed = True`

Interview statuses:
- SCHEDULED
- COMPLETED
- MISSED
- CANCELLED

---

## 13) Visa Issuance and Download

Visa document generation requires:
1. Application in APPROVED state
2. Payment confirmed as PAID
3. If interview required, interview must be completed

Issued visa artifacts:
- Unique visa number
- PDF file
- Issued timestamp
- Issuing actor reference

Download:
- Applicant can download own visa
- Officers/Supervisors/Admins can access for review purposes

---

## 14) Queue and Filtering (Officer Portal)

Queue contains:
- UNDER_REVIEW applications (primary actionable queue)
- PENDING_INFO applications (separate section)

Filtering:
- Queue supports visa-type filtering
- Filter options are loaded from active visa types in database
- Includes quick filters and reset option

---

## 15) Recommendations Engine (Applicant)

Recommendations can include:
- Missing document warnings
- Eligibility warnings from rules engine
- Visa type suggestions based on travel purpose keywords

Purpose keyword mapping:
- business -> BUSINESS
- work/job/employment -> WORK
- study/student/education -> STUDENT
- medical/treatment -> MEDICAL
- conference/seminar -> CONFERENCE
- family/relative -> FAMILY_VISIT

These are advisory suggestions, not automatic changes.

---

## 16) Common User Questions (FAQ Ground Truth)

### Q: Why can I not submit my application?
A: Common reasons include missing passport number, expired/missing passport expiry date, no selected visa type, or no uploaded supporting document.

### Q: Why is my application in Pending Additional Information?
A: A reviewer requested additional details/documents. Upload requested information and the case can return to Under Review.

### Q: Can I upload documents after submission?
A: Document updates are allowed in Draft and Pending Additional Information states.

### Q: When can I pay?
A: Payment is available when your application is Approved.

### Q: Does payment automatically issue visa?
A: In the portal flow, payment confirmation triggers issuance flow, subject to issuance prerequisites.

### Q: Why was I blocked during pre-screening?
A: Nationality rules can hard-block progression. Document/date issues may appear as warnings.

### Q: Can I re-apply after rejection?
A: Yes. Re-apply is available for rejected applications and pre-fills prior details.

### Q: Can I download my visa anytime?
A: You can download once a visa document has been issued for the application.

### Q: Who can review applications?
A: Officer and Supervisor roles.

### Q: Who can manage visa types?
A: Admin role.

---

## 17) Error and Recovery Guidance

If user reports:

### "No payment record found"
- Payment record may not have been created yet.
- User should verify submission completed successfully.

### "Invalid state transition"
- Action attempted in wrong status.
- User should check current status on application detail page.

### "Interview cannot be completed/cancelled"
- Interview must usually be in SCHEDULED state for these actions.

### "I cannot access this page"
- Role-based access controls apply; user may lack permission.

---

## 18) What the Assistant Should Not Do

- Do not provide immigration legal advice beyond system workflow.
- Do not promise approval or fixed processing times.
- Do not fabricate hidden data (internal notes, future decisions, private records).
- Do not claim payment gateway behavior beyond current simulated flow.

---

## 19) Glossary

- **Pre-screening**: Automated rules check after submission.
- **Under Review**: Human reviewer action required.
- **Pending Info**: Awaiting additional applicant information.
- **Approved**: Review decision positive; eligible for payment stage.
- **Issued**: Visa document generated and available.
- **RAG**: Retrieval-Augmented Generation; answers grounded in knowledge base chunks.

---

## 20) Suggested Response Template (for Assistant Consistency)

When answering process questions:
1. Direct answer in one sentence
2. Steps or requirements list
3. Short note on where user can do this in the portal

When uncertain:
- "I do not have enough information in the current knowledge base."
