from rules.engine import get_required_documents


def validate_required_documents(application) -> bool:
    return len(list_missing_documents(application)) == 0


def list_missing_documents(application) -> list[str]:
    # Required list comes from the rule engine, not hardcoded here.
    required = get_required_documents(application.visa_type.code)
    supplied = set(
        application.documents.values_list("document_type", flat=True)
    )
    return [doc for doc in required if doc not in supplied]


def get_document_summary(application) -> dict:
    required = get_required_documents(application.visa_type.code)
    supplied_qs = application.documents.values("document_type", "verified", "uploaded_at")
    supplied_map = {d["document_type"]: d for d in supplied_qs}

    summary = []
    for doc_type in required:
        record = supplied_map.get(doc_type)
        summary.append({
            "document_type": doc_type,
            "uploaded": record is not None,
            "verified": record["verified"] if record else False,
            "uploaded_at": record["uploaded_at"] if record else None,
        })

    return {
        "required": required,
        "summary": summary,
        "all_uploaded": all(item["uploaded"] for item in summary),
        "all_verified": all(item["verified"] for item in summary),
    }
