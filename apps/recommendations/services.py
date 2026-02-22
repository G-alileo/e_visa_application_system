from dataclasses import dataclass


@dataclass
class Recommendation:
    type: str
    message: str
    explanation: str

    def as_dict(self) -> dict:
        return {
            "type": self.type,
            "message": self.message,
            "explanation": self.explanation,
        }


def get_recommendations(application) -> list[dict]:
    recommendations: list[Recommendation] = []

    recommendations.extend(_document_recommendations(application))
    recommendations.extend(_eligibility_recommendations(application))
    recommendations.extend(_visa_type_recommendations(application))

    return [r.as_dict() for r in recommendations]


def _document_recommendations(application) -> list[Recommendation]:
    # Advisory only — submission is not blocked by missing documents.
    from apps.documents.services import list_missing_documents

    missing = list_missing_documents(application)
    if not missing:
        return []

    return [
        Recommendation(
            type="MISSING_DOCUMENT_WARNING",
            message=f"Document '{doc}' is required but has not been uploaded.",
            explanation=(
                f"Your visa type ({application.visa_type.code}) requires a '{doc}'. "
                "Uploading it before submission reduces the chance of your application "
                "being paused for more information."
            ),
        )
        for doc in missing
    ]


def _eligibility_recommendations(application) -> list[Recommendation]:
    # Nationality hard-blocks appear here as warnings; they are enforced
    # definitively (and raised as exceptions) during run_pre_screening().
    import datetime
    from rules.engine import evaluate

    supplied_types = list(
        application.documents.values_list("document_type", flat=True)
    )

    result = evaluate(
        visa_type_code=application.visa_type.code,
        nationality=application.nationality,
        intended_entry_date=application.intended_entry_date,
        supplied_document_types=supplied_types,
    )

    if result.passed:
        return []

    recs = []
    for code, explanation in zip(result.failure_codes, result.explanations):
        recs.append(
            Recommendation(
                type=f"ELIGIBILITY_WARNING_{code}",
                message="Potential eligibility issue detected.",
                explanation=explanation,
            )
        )
    return recs


def _visa_type_recommendations(application) -> list[Recommendation]:
    from apps.visas.models import VisaType

    purpose = (application.purpose_of_travel or "").lower()
    current_code = application.visa_type.code
    recs = []

    keyword_map = {
        "business": "BUSINESS_90",
        "work": "BUSINESS_90",
        "study": "STUDENT_365",
        "student": "STUDENT_365",
        "education": "STUDENT_365",
    }

    for keyword, suggested_code in keyword_map.items():
        if keyword in purpose and suggested_code != current_code:
            suggested = VisaType.objects.filter(code=suggested_code, is_active=True).first()
            if suggested:
                recs.append(
                    Recommendation(
                        type="VISA_TYPE_SUGGESTION",
                        message=f"Consider visa type '{suggested.name}' ({suggested_code}).",
                        explanation=(
                            f"Your stated purpose of travel mentions '{keyword}'. "
                            f"The '{suggested.name}' visa type may be more appropriate "
                            f"than your current selection ({current_code}). "
                            "This is a suggestion only — your current selection is still valid."
                        ),
                    )
                )
            break  # only one suggestion per application

    return recs
