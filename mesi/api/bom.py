# your_app/api/mes.py

import frappe
import requests

import frappe
import requests
from mesint.mes_intergration.api.log import write_log

@frappe.whitelist()
def sync_bom(bom_no):

    settings = frappe.get_single("Mes Setting")

    token = settings.get_password("access_token")

    url = (
        settings.mes_url.rstrip("/")
        + "/MMS/API/V1/Customer/Command/BOM/Insert/Bulk"
    )

    bom = frappe.get_doc("BOM", bom_no)

    child_info = []

    for row in bom.items:
        log = frappe.db.exists(
            "MES Log",
            {
                "document_type": "Item",
                "document_name": row.item_code,
                "status": "Success"
            }
        )

        if not log:
            frappe.throw(
                f"Item {row.item_code} chưa đồng bộ lên MES."
            )
            
        child_info.append({
            "childMaterialBomRemark": row.description or "",
            "childMaterialBomUnit": float(row.qty),
            "childMaterialPartNumber": row.item_code
        })

    body = {
        "data": [
            {
                "materialPartNumber": bom.item,
                "childInfo": child_info
            }
        ]
    }

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
            api_name="BOM Insert Bulk",
            document_type="BOM",
            document_name=bom.name,
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
            api_name="BOM Insert Bulk",
            document_type="BOM",
            document_name=bom.name,
            request_body=body,
            status="Failed",
            error_message=str(e)
        )

        raise

@frappe.whitelist()
def sync_all_bom():

    settings = frappe.get_single("Mes Setting")

    token = settings.get_password("access_token")

    url = (
        settings.mes_url.rstrip("/")
        + "/MMS/API/V1/Customer/Command/BOM/Insert/Bulk"
    )

    body = {
        "data": []
    }

    boms = frappe.get_all(
        "BOM",
        filters={
            "is_active": 1,
            "docstatus": 1
        },
        pluck="name"
    )

    for bom_name in boms:

        bom = frappe.get_doc("BOM", bom_name)

        children = []

        for row in bom.items:

            children.append({
                "childMaterialBomRemark": row.description or "",
                "childMaterialBomUnit": float(row.qty),
                "childMaterialPartNumber": row.item_code
            })

        body["data"].append({
            "materialPartNumber": bom.item,
            "childInfo": children
        })

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=body,
        headers=headers,
        timeout=120
    )

    result = response.json()

    write_log(
        api_name="BOM Insert Bulk",
        document_type="BOM",
        document_name="ALL",
        request_body=body,
        response_body=result,
        status="Success",
        http_status=response.status_code
    )

    response.raise_for_status()

    return result