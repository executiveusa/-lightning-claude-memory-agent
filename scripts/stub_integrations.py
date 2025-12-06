#!/usr/bin/env python3
"""
Railway Zero-Secrets Bootstrapper - Integration Stubbing Script

This script helps disable or safely stub optional third-party integrations
that require secrets, enabling zero-secrets deployment to Railway.

Usage:
    python scripts/stub_integrations.py --check
    python scripts/stub_integrations.py --stub tinker wandb
    python scripts/stub_integrations.py --restore
"""

import argparse
import json
import os
import sys
from pathlib import Path


class IntegrationStubber:
    """Manages stubbing of optional integrations for zero-secrets deployment."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.agents_file = repo_root / ".agents"
        self.integrations = self._load_integrations()

    def _load_integrations(self) -> dict:
        """Load integration definitions from .agents file."""
        if not self.agents_file.exists():
            print(f"Error: .agents file not found at {self.agents_file}")
            sys.exit(1)

        with open(self.agents_file) as f:
            data = json.load(f)

        return data.get("modules", {})

    def check_status(self) -> dict:
        """Check which integrations have secrets configured."""
        status = {}

        for module_name, module_info in self.integrations.items():
            if module_name == "core":
                continue  # Skip core - always required

            secrets = module_info.get("secrets", [])
            configured = []
            missing = []

            for secret in secrets:
                if os.getenv(secret):
                    configured.append(secret)
                else:
                    missing.append(secret)

            status[module_name] = {
                "name": module_info.get("name", module_name),
                "configured": configured,
                "missing": missing,
                "stub_mode": module_info.get("stub_mode", "No stub available"),
                "is_stubbed": len(missing) == len(secrets),
            }

        return status

    def print_status(self):
        """Print current integration status."""
        print("\n" + "=" * 70)
        print("RAILWAY ZERO-SECRETS DEPLOYMENT - INTEGRATION STATUS")
        print("=" * 70 + "\n")

        status = self.check_status()

        for module_name, info in status.items():
            icon = "✅" if not info["is_stubbed"] else "🔧"
            state = "CONFIGURED" if not info["is_stubbed"] else "STUBBED"

            print(f"{icon} {info['name']} - {state}")

            if info["configured"]:
                print(f"   Configured: {', '.join(info['configured'])}")

            if info["missing"]:
                print(f"   Missing: {', '.join(info['missing'])}")
                print(f"   Stub Mode: {info['stub_mode']}")

            print()

        # Summary
        total = len(status)
        stubbed = sum(1 for s in status.values() if s["is_stubbed"])
        configured = total - stubbed

        print("-" * 70)
        print(f"Summary: {configured}/{total} integrations configured, {stubbed}/{total} stubbed")
        print("-" * 70 + "\n")

    def generate_env_template(self, output_file: Path = None):
        """Generate .env.template with safe defaults."""
        if output_file is None:
            output_file = self.repo_root / ".env.railway.template"

        lines = [
            "# Railway Zero-Secrets Deployment - Environment Template",
            "# This file shows all available environment variables with safe defaults",
            "# Copy values from master.secrets.json as needed",
            "",
            "# ===== CORE SECRETS (REQUIRED) =====",
        ]

        # Load from .agents
        try:
            with open(self.agents_file) as f:
                agents_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: .agents file not found at {self.agents_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: .agents file is not valid JSON: {e}")
            sys.exit(1)

        # Core secrets
        for secret in agents_data.get("core", []):
            name = secret["name"]
            description = secret["description"]
            default = secret.get("default", "")
            lines.extend([
                f"# {description}",
                f"{name}={default}",
                "",
            ])

        # Optional secrets
        lines.extend([
            "# ===== OPTIONAL INTEGRATIONS =====",
            "# Leave empty or use defaults to stub these integrations",
            "",
        ])

        for secret in agents_data.get("optional", []):
            name = secret["name"]
            description = secret["description"]
            default = secret.get("default", "")
            module = secret.get("module", "")
            disabled = secret.get("disabled_behavior", "")
            lines.extend([
                f"# {description}",
                f"# Module: {module}",
                f"# When empty: {disabled}",
                f"{name}={default}",
                "",
            ])

        # Runtime config
        lines.extend([
            "# ===== RUNTIME CONFIGURATION =====",
            "",
        ])

        for secret in agents_data.get("runtime", []):
            name = secret["name"]
            description = secret["description"]
            default = secret.get("default", "")
            lines.extend([
                f"# {description}",
                f"{name}={default}",
                "",
            ])

        # Write file
        try:
            with open(output_file, "w") as f:
                f.write("\n".join(lines))
            print(f"✅ Environment template generated: {output_file}")
        except IOError as e:
            print(f"Error: Failed to write template file: {e}")
            sys.exit(1)

    def validate_secrets(self) -> bool:
        """Validate that required secrets are configured."""
        with open(self.agents_file) as f:
            agents_data = json.load(f)

        required = agents_data.get("required_secrets", [])
        missing = []

        for secret in required:
            if not os.getenv(secret):
                missing.append(secret)

        if missing:
            print("\n❌ VALIDATION FAILED - Missing required secrets:")
            for secret in missing:
                print(f"   - {secret}")
            print("\nSet these in Railway dashboard or local environment.")
            return False
        else:
            print("\n✅ VALIDATION PASSED - All required secrets configured")
            return True


def main():
    parser = argparse.ArgumentParser(
        description="Railway Zero-Secrets Integration Stubber",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check current integration status",
    )

    parser.add_argument(
        "--generate-env",
        action="store_true",
        help="Generate .env template with safe defaults",
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate required secrets are configured",
    )

    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    stubber = IntegrationStubber(repo_root)

    if args.check:
        stubber.print_status()
    elif args.generate_env:
        stubber.generate_env_template()
    elif args.validate:
        is_valid = stubber.validate_secrets()
        sys.exit(0 if is_valid else 1)
    else:
        # Default: show status
        stubber.print_status()


if __name__ == "__main__":
    main()
