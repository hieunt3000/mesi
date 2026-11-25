import frappe
import json


def write_log(
    api_name,
    document_type,
    document_name,
    request_body,
    response_body=None,
    status="Success",
    http_status=200,
    error_message=None
):
    log = frappe.new_doc("Mes Log")

    log.api_name = api_name
    log.document_type = document_type
    log.document_name = document_name
    log.request_body = json.dumps(
        request_body,
        ensure_ascii=False,
        indent=2
    )

    if response_body:
        log.response_body = json.dumps(
            response_body,
            ensure_ascii=False,
            indent=2
        )

    log.status = status
    log.http_status = http_status
    log.error_message = error_message

    log.insert(ignore_permissions=True)
    frappe.db.commit()