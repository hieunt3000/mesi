import frappe
import requests

from mesint.mes_intergration.api.log import write_log


@frappe.whitelist()
def sync_route(routing_name):

    settings = frappe.get_single("MES Setting")

    token = settings.get_password("access_token")

    url = (
        settings.mes_url.rstrip("/")
        + "/PDM/API/V1/Customer/Common/CompositeRoute/UpsertBatch"
    )

    routing = frappe.get_doc("Routing", routing_name)

    body = []

    for row in routing.operations:

        body.append({
            "productNumber": routing.item or "",
            "productRouteName": routing.name,
            "isDefaultRoute": True,
            "productRouteRemarks": routing.notes or "",
            "processNumber": row.operation
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

        response.raise_for_status()

        if result.get("code") != 0:
            frappe.throw(result.get("message"))

        write_log(
            api_name="CompositeRoute UpsertBatch",
            document_type="Routing",
            document_name=routing.name,
            request_body=body,
            response_body=result,
            status="Success",
            http_status=response.status_code
        )

        return result

    except Exception as e:

        write_log(
            api_name="CompositeRoute UpsertBatch",
            document_type="Routing",
            document_name=routing.name,
            request_body=body,
            status="Failed",
            error_message=str(e)
        )

        raise