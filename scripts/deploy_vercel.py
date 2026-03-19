#!/usr/bin/env python3
"""
Vercel Deployment Agent for OGOS SaaS Platform.

This script automates the deployment of both backend (FastAPI) and frontend (Next.js)
to Vercel, handling environment variables, project linking, and deployment verification.

Usage:
    python scripts/deploy_vercel.py [--backend-only | --frontend-only] [--prod]

Requirements:
    - Vercel CLI installed: npm i -g vercel
    - Logged into Vercel: vercel login
    - GitHub repo already pushed
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    success: bool
    url: Optional[str] = None
    error: Optional[str] = None
    project_name: Optional[str] = None


class VercelDeployAgent:
    """Agent for deploying to Vercel."""

    def __init__(self, root_dir: Path, verbose: bool = True):
        self.root_dir = root_dir
        self.frontend_dir = root_dir / "frontend"
        self.verbose = verbose
        self.backend_url: Optional[str] = None
        self.frontend_url: Optional[str] = None

    def log(self, message: str, level: str = "info") -> None:
        """Log a message with color coding."""
        colors = {
            "info": "\033[94m",
            "success": "\033[92m",
            "warning": "\033[93m",
            "error": "\033[91m",
            "reset": "\033[0m",
        }
        if self.verbose:
            prefix = {
                "info": "ℹ️ ",
                "success": "✅",
                "warning": "⚠️ ",
                "error": "❌",
            }.get(level, "")
            print(f"{colors.get(level, '')}{prefix} {message}{colors['reset']}")

    def run_command(
        self,
        cmd: list[str],
        cwd: Optional[Path] = None,
        capture: bool = True,
        env: Optional[dict] = None,
    ) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        working_dir = cwd or self.root_dir
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        if self.verbose:
            self.log(f"Running: {' '.join(cmd)}", "info")

        result = subprocess.run(
            cmd,
            cwd=working_dir,
            capture_output=capture,
            text=True,
            env=full_env,
        )
        return result.returncode, result.stdout, result.stderr

    def check_vercel_cli(self) -> bool:
        """Check if Vercel CLI is installed and authenticated."""
        code, stdout, _ = self.run_command(["npx", "vercel", "--version"])
        if code != 0:
            self.log("Vercel CLI not found. Run: npm install", "error")
            return False

        self.log(f"Vercel CLI version: {stdout.strip()}", "success")

        code, stdout, stderr = self.run_command(["npx", "vercel", "whoami"])
        if code != 0:
            self.log("Not logged into Vercel.", "warning")
            self.log("", "info")
            self.log("To login, run this command in your terminal:", "info")
            self.log("  npx vercel login", "info")
            self.log("", "info")
            self.log("This will open a browser for authentication.", "info")
            self.log("After logging in, run this deploy script again.", "info")
            return False

        self.log(f"Logged in as: {stdout.strip()}", "success")
        return True

    def check_env_file(self, is_frontend: bool = False) -> dict[str, str]:
        """Check for environment variables and return them."""
        if is_frontend:
            env_file = self.frontend_dir / ".env.local"
            example_file = self.frontend_dir / ".env.local.example"
        else:
            env_file = self.root_dir / ".env"
            example_file = self.root_dir / ".env.vercel.example"

        env_vars = {}

        if env_file.exists():
            self.log(f"Found {env_file.name}", "success")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
        else:
            self.log(f"No {env_file.name} found. Using example file.", "warning")
            if example_file.exists():
                self.log(f"See {example_file.name} for required variables", "info")

        return env_vars

    def get_required_env_vars(self, is_frontend: bool = False) -> list[str]:
        """Get list of required environment variables."""
        if is_frontend:
            return [
                "NEXT_PUBLIC_API_URL",
                "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
            ]
        return [
            "CLERK_SECRET_KEY",
            "STRIPE_API_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "OGOS_BASE_URL",
            "OGOS_API_KEY",
        ]

    def deploy_backend(self, prod: bool = False) -> DeploymentResult:
        """Deploy the FastAPI backend to Vercel."""
        self.log("=" * 50, "info")
        self.log("Deploying Backend (FastAPI)", "info")
        self.log("=" * 50, "info")

        if not (self.root_dir / "vercel.json").exists():
            self.log("vercel.json not found in root directory", "error")
            return DeploymentResult(success=False, error="Missing vercel.json")

        env_vars = self.check_env_file(is_frontend=False)
        required = self.get_required_env_vars(is_frontend=False)
        missing = [v for v in required if v not in env_vars]

        if missing:
            self.log(f"Missing env vars: {', '.join(missing)}", "warning")
            self.log("You'll need to add these in Vercel dashboard", "warning")

        cmd = ["npx", "vercel", "--yes"]
        if prod:
            cmd.append("--prod")

        code, stdout, stderr = self.run_command(cmd, cwd=self.root_dir)

        if code != 0:
            self.log(f"Backend deployment failed: {stderr}", "error")
            return DeploymentResult(success=False, error=stderr)

        url = self._extract_url(stdout)
        self.backend_url = url
        self.log(f"Backend deployed: {url}", "success")

        return DeploymentResult(
            success=True,
            url=url,
            project_name="ogos-saas-api",
        )

    def deploy_frontend(self, prod: bool = False) -> DeploymentResult:
        """Deploy the Next.js frontend to Vercel."""
        self.log("=" * 50, "info")
        self.log("Deploying Frontend (Next.js)", "info")
        self.log("=" * 50, "info")

        if not self.frontend_dir.exists():
            self.log("Frontend directory not found", "error")
            return DeploymentResult(success=False, error="Missing frontend directory")

        env_vars = self.check_env_file(is_frontend=True)

        if self.backend_url and "NEXT_PUBLIC_API_URL" not in env_vars:
            self.log(f"Setting API URL to: {self.backend_url}", "info")

        cmd = ["npx", "vercel", "--yes"]
        if prod:
            cmd.append("--prod")

        env = {}
        if self.backend_url:
            env["NEXT_PUBLIC_API_URL"] = self.backend_url

        code, stdout, stderr = self.run_command(
            cmd, cwd=self.frontend_dir, env=env if env else None
        )

        if code != 0:
            self.log(f"Frontend deployment failed: {stderr}", "error")
            return DeploymentResult(success=False, error=stderr)

        url = self._extract_url(stdout)
        self.frontend_url = url
        self.log(f"Frontend deployed: {url}", "success")

        return DeploymentResult(
            success=True,
            url=url,
            project_name="ogos-saas-frontend",
        )

    def _extract_url(self, output: str) -> Optional[str]:
        """Extract deployment URL from Vercel output."""
        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("https://") and ".vercel.app" in line:
                return line
            if line.startswith("https://") and not line.startswith("https://vercel.com"):
                return line
        return None

    def verify_deployment(self, url: str, endpoint: str = "/healthz") -> bool:
        """Verify a deployment is working."""
        import urllib.request
        import urllib.error

        full_url = f"{url}{endpoint}"
        self.log(f"Verifying: {full_url}", "info")

        try:
            with urllib.request.urlopen(full_url, timeout=30) as response:
                if response.status == 200:
                    self.log(f"Health check passed: {response.status}", "success")
                    return True
                self.log(f"Health check returned: {response.status}", "warning")
                return False
        except urllib.error.URLError as e:
            self.log(f"Health check failed: {e}", "error")
            return False
        except Exception as e:
            self.log(f"Verification error: {e}", "error")
            return False

    def print_summary(self) -> None:
        """Print deployment summary."""
        self.log("=" * 50, "info")
        self.log("DEPLOYMENT SUMMARY", "info")
        self.log("=" * 50, "info")

        if self.backend_url:
            self.log(f"Backend API:  {self.backend_url}", "success")
            self.log(f"  Health:     {self.backend_url}/healthz", "info")
            self.log(f"  Beer API:   {self.backend_url}/beer/label-types", "info")

        if self.frontend_url:
            self.log(f"Frontend:     {self.frontend_url}", "success")

        self.log("", "info")
        self.log("NEXT STEPS:", "info")
        self.log("1. Add environment variables in Vercel Dashboard", "info")
        self.log("2. Configure Stripe webhook endpoint", "info")
        self.log("3. Set up Clerk allowed origins", "info")
        self.log("4. Test the beer labels API", "info")

    def deploy_all(self, prod: bool = False) -> bool:
        """Deploy both backend and frontend."""
        if not self.check_vercel_cli():
            return False

        backend_result = self.deploy_backend(prod=prod)
        if not backend_result.success:
            self.log("Backend deployment failed, aborting", "error")
            return False

        frontend_result = self.deploy_frontend(prod=prod)
        if not frontend_result.success:
            self.log("Frontend deployment failed", "error")
            return False

        if self.backend_url:
            self.log("Waiting for deployment to propagate...", "info")
            import time
            time.sleep(5)
            self.verify_deployment(self.backend_url)

        self.print_summary()
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy OGOS SaaS Platform to Vercel"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Deploy only the backend API",
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Deploy only the frontend",
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Deploy to production (default is preview)",
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        help="Backend URL for frontend deployment (if deploying frontend only)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity",
    )

    args = parser.parse_args()

    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    agent = VercelDeployAgent(root_dir, verbose=not args.quiet)

    if not agent.check_vercel_cli():
        sys.exit(1)

    if args.backend_only:
        result = agent.deploy_backend(prod=args.prod)
        if result.success:
            agent.print_summary()
        sys.exit(0 if result.success else 1)

    if args.frontend_only:
        if args.backend_url:
            agent.backend_url = args.backend_url
        result = agent.deploy_frontend(prod=args.prod)
        if result.success:
            agent.print_summary()
        sys.exit(0 if result.success else 1)

    success = agent.deploy_all(prod=args.prod)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
