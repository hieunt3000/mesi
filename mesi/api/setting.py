import frappe
import requests

@frappe.whitelist()
def get_token():
   
    settings = frappe.get_single("Mes Setting")
    # return "Test"
    payload = {
        "account": settings.account,
        "password": settings.get_password("password")
    }
    
    response = requests.post(
        f"{settings.mes_url}/privatecloudcore/API/V1/Customer/Auth/Login",
        json=payload,
        headers={
            "Content-Type": "application/json"
        },
        timeout=settings.timeout
    )

    response.raise_for_status()

    result = response.json()

    if result.get("code") != 0:
        frappe.throw(result.get("message", "Get token failed"))

    content = result.get("content", {})

    settings.access_token = content.get("accessToken")
    settings.refresh_token = content.get("refreshToken")

    settings.save(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "message": result.get("message"),
        "access_token": content.get("accessToken")
    }
@frappe.whitelist()
def test_connection():

    settings = frappe.get_single("Mes Setting")

    headers = {
        "Authorization":
        f"Bearer {settings.get_password('access_token')}"
    }

    r = requests.get(
        f"{settings.mes_url}/health",
        headers=headers
    )

    return r.json()