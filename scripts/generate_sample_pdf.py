from pathlib import Path

import fitz


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[1] / "sample_data"
SOURCE_OUTPUT_PATH = SAMPLE_DATA_DIR / "synthetic_medical_record_source.pdf"
DEIDENTIFIED_OUTPUT_PATH = SAMPLE_DATA_DIR / "deidentified_medical_record.pdf"
MARGIN = 54
PAGE_WIDTH = 612
PAGE_HEIGHT = 792
TEXTBOX = fitz.Rect(MARGIN, MARGIN, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN)


PAGE_ONE = """
SYNTHETIC MEDICAL RECORD
For product demonstration only. All names, dates, and identifiers below are fictional.

Patient Name: Evelyn Carter
Date of Birth: 04/18/1982
Medical Record Number: MRN-48291
Patient ID: PT-003184
Home Address: 1482 Willow Bend Drive, Nashville, TN 37212
Phone: (615) 555-0142
Email: evelyn.carter@example.com
Primary Care Physician: Daniel Nguyen, MD
Encounter Date: 03/04/2026
Facility: Rivergate Family Medicine

Chief Complaint:
Persistent dry cough, fatigue, and intermittent shortness of breath for 12 days.

History of Present Illness:
Patient reports worsening cough at night and low-grade fever over the weekend.
No prior pneumonia history. Denies chest pain. Works as a paralegal and reports recent travel.

Vital Signs:
Blood Pressure: 146/92
Pulse: 88
Temperature: 99.4 F
Respiratory Rate: 18
Oxygen Saturation: 97%

Assessment:
1. Acute bronchitis
2. Mild hypertension
3. Sleep disruption due to cough
""".strip()

PAGE_TWO = """
Plan of Care:
- Prescribed azithromycin 250 mg for 5 days.
- Prescribed benzonatate 100 mg up to three times daily as needed for cough.
- Continue lisinopril 10 mg daily.
- Encourage hydration and rest.
- Follow up in 2 weeks or sooner if symptoms worsen.

Diagnostics:
Chest X-ray ordered for persistent cough.
CBC and CMP ordered.

Visit Summary:
Patient advised to return if fever exceeds 101.5 F, breathing worsens, or chest pain develops.
March follow-up should review cough resolution, medication tolerance, and blood pressure control.

Insurance:
Member ID: UH-55612098
Group Number: G-20491
Claim Contact: 800-555-0199

Emergency Contact:
Mason Carter
Relationship: Spouse
Phone: (615) 555-0187
""".strip()


DEIDENTIFIED_PAGE_ONE = """
SYNTHETIC DE-IDENTIFIED MEDICAL RECORD
For product demonstration only. This record is synthetic and formatted to align with HIPAA Safe Harbor style removal of direct patient identifiers.

Patient: [REMOVED]
Age Range: 40-45
Record Number: [REMOVED]
Patient ID: [REMOVED]
Geographic Detail: Tennessee
Contact Information: [REMOVED]
Encounter Year: 2026
Care Setting: Primary Care

Chief Complaint:
Persistent dry cough, fatigue, and intermittent shortness of breath for approximately two weeks.

History of Present Illness:
Patient reports worsening cough at night and low-grade fever over a recent weekend.
No prior pneumonia history. Denies chest pain. Recent travel reported.

Vital Signs:
Blood Pressure: 146/92
Pulse: 88
Temperature: 99.4 F
Respiratory Rate: 18
Oxygen Saturation: 97%

Assessment:
1. Acute bronchitis
2. Mild hypertension
3. Sleep disruption due to cough
""".strip()


DEIDENTIFIED_PAGE_TWO = """
Plan of Care:
- Prescribed azithromycin 250 mg for 5 days.
- Prescribed benzonatate 100 mg up to three times daily as needed for cough.
- Continue lisinopril 10 mg daily.
- Encourage hydration and rest.
- Follow up in approximately 2 weeks or sooner if symptoms worsen.

Diagnostics:
Chest X-ray ordered for persistent cough.
CBC and CMP ordered.

Visit Summary:
Patient advised to return if fever exceeds 101.5 F, breathing worsens, or chest pain develops.
Follow-up should review cough resolution, medication tolerance, and blood pressure control.

Administrative Details:
Insurance member details removed.
Emergency contact details removed.
""".strip()


def add_page(document: fitz.Document, text: str) -> None:
    page = document.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    page.insert_textbox(TEXTBOX, text, fontsize=12, fontname="helv", lineheight=1.35)


def write_document(output_path: Path, pages: list[str]) -> None:
    document = fitz.open()
    for page_text in pages:
        add_page(document, page_text)
    document.save(output_path)


def main() -> None:
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_document(SOURCE_OUTPUT_PATH, [PAGE_ONE, PAGE_TWO])
    write_document(DEIDENTIFIED_OUTPUT_PATH, [DEIDENTIFIED_PAGE_ONE, DEIDENTIFIED_PAGE_TWO])
    print(f"Wrote {SOURCE_OUTPUT_PATH}")
    print(f"Wrote {DEIDENTIFIED_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
