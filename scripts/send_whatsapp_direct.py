#!/usr/bin/env python3
"""Send WhatsApp messages via MCP using JSON-RPC.
This script is intended to be used inside Kestra Python tasks.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import requests


def send_whatsapp_message(phone_number: str, message: str, whatsapp_mcp_url: str) -> Dict[str, Any]:
    """Send a WhatsApp text message using the MCP JSON-RPC endpoint.

    Args:
        phone_number: Destination phone number in E.164 format.
        message: Message text to send.
        whatsapp_mcp_url: Base URL of the WhatsApp MCP server (without trailing /mcp).

    Returns:
        Dictionary containing status code, body, success flag and headers.
    """
    mcp_url = f"{whatsapp_mcp_url.rstrip('/')}/mcp"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "sendTextMessage",
            "arguments": {
                "to": phone_number,
                "message": message,
            },
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Kestra-WhatsApp-Script/1.0",
    }

    print(f"[INFO] Enviando mensagem para {phone_number} via {mcp_url}…")
    try:
        response = requests.post(mcp_url, json=payload, headers=headers, timeout=60)
    except Exception as exc:  # pragma: no cover – network failure
        error_msg = f"Erro de requisição: {exc}"
        print(f"[ERROR] {error_msg}")
        return {"statusCode": 500, "body": error_msg, "success": False, "headers": {}}

    try:
        body = response.json()
    except ValueError:
        body = response.text

    success = response.status_code == 200
    print(f"[INFO] Status {response.status_code} – Sucesso={success}\n{json.dumps(body, ensure_ascii=False, indent=2) if isinstance(body, dict) else body}")

    return {
        "statusCode": response.status_code,
        "body": json.dumps(body) if isinstance(body, (dict, list)) else str(body),
        "success": success,
        "headers": dict(response.headers),
    }


def main() -> None:  # pragma: no cover
    """Entrypoint quando chamado como script dentro do Kestra."""
    phone = os.getenv("PHONE_NUMBER", "")
    message = os.getenv("MESSAGE", "")
    whatsapp_mcp_url = os.getenv("WHATSAPP_MCP_URL", "")

    if not all([phone, message, whatsapp_mcp_url]):
        print("[ERROR] PHONE_NUMBER, MESSAGE ou WHATSAPP_MCP_URL não definidos.")
        sys.exit(1)

    from kestra import Kestra  # type: ignore

    result = send_whatsapp_message(phone, message, whatsapp_mcp_url)
    Kestra.outputs(result)


if __name__ == "__main__":
    main()

