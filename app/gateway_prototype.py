from __future__ import annotations

import argparse
import asyncio
import json

from app.gateway_client import GatewayClient, GatewayClientError, GatewayRequestError
from app.gateway_config import GatewaySettings
from app.gateway_identity import load_or_create_identity
from app.gateway_protocol import GatewayProtocolError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only OpenClaw Gateway client prototype"
    )
    parser.add_argument(
        "--sessions",
        action="store_true",
        help="List a bounded set of sessions after connecting",
    )
    parser.add_argument(
        "--history",
        metavar="SESSION_KEY",
        help="Read bounded chat history for one session",
    )
    return parser


async def run(args: argparse.Namespace) -> None:
    settings = GatewaySettings.from_environment()
    identity = load_or_create_identity()
    async with GatewayClient(settings=settings, identity=identity) as client:
        assert client.hello is not None
        server = client.hello.get("server")
        features = client.hello.get("features")
        summary = {
            "protocol": client.hello.get("protocol"),
            "serverVersion": server.get("version") if isinstance(server, dict) else None,
            "grantedScopes": client.hello.get("auth", {}).get("scopes"),
            "methodCount": len(features.get("methods", []))
            if isinstance(features, dict)
            else 0,
        }
        print(json.dumps(summary, indent=2))
        if args.sessions:
            print(json.dumps(await client.sessions_list(limit=25), indent=2))
        if args.history:
            print(
                json.dumps(
                    await client.chat_history(args.history, limit=50, max_chars=50_000),
                    indent=2,
                )
            )


def main() -> int:
    args = build_parser().parse_args()
    try:
        asyncio.run(run(args))
    except GatewayRequestError as error:
        print(f"Gateway prototype failed safely: {error.code or 'gateway_request_error'}")
        return 1
    except (GatewayClientError, GatewayProtocolError, ValueError) as error:
        print(f"Gateway prototype failed safely: {type(error).__name__}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
