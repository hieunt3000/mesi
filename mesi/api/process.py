import frappe
import requests

from mesint.mes_intergration.api.log import write_log


@frappe.whitelist()
def sync_process(operation_name):

    settings = frappe.get_single("MES Setting")

    token = settings.get_password("access_token")

    url = (
        settings.mes_url.rstrip("/")
        + "/PDM/API/V1/Customer/Common/CompositeProcess/UpsertBatch"
    )

    operation = frappe.get_doc("Operation", operation_name)

    body = [{
        "processNumber": operation.name,
        "processName": operation.operation_name,
        "processTypeId": 1,
        "makeTypeId": 1,
        "defaultIsCriticalProcess": True,
        "customValues": [],
        "resourceType": 4,
        "resourceName": ""
    }]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=60
        )

        result = response.json()

        write_log(
            api_name="CompositeProcess UpsertBatch",
            document_type="Operation",
            document_name="ALL",
            request_body=body,
            response_body=result,
            status="Success",
            http_status=response.status_code
        )

        response.raise_for_status()

        if result.get("code") != 0:
            frappe.throw(result.get("message"))

        return result

    except Exception as e:

        write_log(
            api_name="CompositeProcess UpsertBatch",
            document_type="Operation",
            document_name="ALL",
            request_body=body,
            status="Failed",
            error_message=str(e)
        )

        raise
        
@frappe.whitelist()
def sync_all_process():

    settings = frappe.get_single("MES Setting")

    token = settings.get_password("access_token")

    url = (
        settings.mes_url.rstrip("/")
        + "/PDM/API/V1/Customer/Common/CompositeProcess/UpsertBatch"
    )

    operations = frappe.get_all(
        "Operation",
        fields=[
            "name",
            "operation_name"
        ]
    )

    body = []

    for op in operations:

        body.append({
            "processNumber": op.name,
            "processName": op.operation_name,
            "processTypeId": 1,
            "makeTypeId": 1,
            "defaultIsCriticalProcess": True,
            "customValues": [],
            "resourceType": 4,
            "resourceName": ""
        })

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            url,
            json=body,
            headers=headers,
            timeout=60
        )

        result = response.json()

        write_log(
            api_name="CompositeProcess UpsertBatch",
            document_type="Operation",
            document_name="ALL",
            request_body=body,
            response_body=result,
            status="Success",
            http_status=response.status_code
        )

        response.raise_for_status()

        if result.get("code") != 0:
            frappe.throw(result.get("message"))

        return result

    except Exception as e:

        write_log(
            api_name="CompositeProcess UpsertBatch",
            document_type="Operation",
            document_name="ALL",
            request_body=body,
            status="Failed",
            error_message=str(e)
        )

        raise        