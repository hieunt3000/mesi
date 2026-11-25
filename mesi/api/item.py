# your_app/api/mes.py

import frappe
import requests

import frappe
import requests
from mesint.mes_intergration.api.log import write_log

@frappe.whitelist()
def sync_item(item_code):
    # Lấy Item
    item = frappe.get_doc("Item", item_code)

    # Lấy cấu hình MES
    settings = frappe.get_single("Mes Setting")
    token = settings.get_password("access_token")

    url = settings.mes_url.rstrip("/") + "/MMS/API/V1/Customer/Command/Material/UpsertBatch"

    body = {
        "dto": {
            "materials": [
                {
                    "materialPartNumber": item.item_code,
                    "materialName": item.item_name,
                    "materialSpec": item.description or "",
                    "materialUnit": item.stock_uom,
                    "materialTypeName": item.item_group or None,
                    "materialProperty": 1,
                    "materialState": 1 if not item.disabled else 0,
                    "reorderPoint": 0,
                    "inventoryReplenishmentAmount": 0,
                    "mainSupplierName": None,
                    "deliveryDay": 0,
                    "materialDescribe": item.description,
                    "safetyStock": None
                }
            ]
        }
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
            api_name="Material UpsertBatch",
            document_type="Item",
            document_name=item.name,
            request_body=body,
            response_body=result,
            status="Success",
            http_status=response.status_code
        )
        # frappe.msgprint("Write Log")
        return result

    except Exception as e:

        write_log(
            api_name="Material UpsertBatch",
            document_type="Item",
            document_name=item.name,
            request_body=body,
            status="Failed",
            error_message=str(e)
        )

        raise
