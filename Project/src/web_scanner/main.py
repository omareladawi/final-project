#!/usr/bin/env python3
import argparse
import asyncio
import colorlog
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config.scanner_config import ScannerConfig, load_scanner_config
from .reporting.report_generator import generate_report
from .scanner.vulnerability_scanner import VulnerabilityScanner as Scanner


def get_app_dir() -> Path:
    """Return the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO

    handler = colorlog.StreamHandler(stream=sys.stdout)
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s[%(levelname)s]%(reset)s "
            "%(yellow)s%(asctime)s%(reset)s: "
            "%(blue)s%(message)s%(reset)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    ))
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.basicConfig(level=level, handlers=[handler], force=True)


def normalize_target_url(url: str) -> str:
    """Ensure a scheme is present before scanning."""
    return url if url.startswith(("http://", "https://")) else f"https://{url}"


def build_runtime_config(args: argparse.Namespace) -> ScannerConfig:
    """Combine defaults, YAML, and CLI values into one config object."""
    config_data = load_scanner_config(args.config) if args.config else ScannerConfig()
    
    # Normalize auth_url - handle shell expansion issues on Windows
    auth_url = args.auth_url or ""
    if auth_url:
        # Convert backslashes to forward slashes and remove drive letters (Windows file path artifacts)
        auth_url = auth_url.replace("\\", "/")
        if ":" in auth_url and auth_url[1] == ":":  # Remove C: style drive letters
            auth_url = "/" + auth_url[2:].lstrip("/")
        auth_url = auth_url.replace("%20", "-").replace(" ", "-")  # Clean spaces
    
    config_updates = {
        "target_url": normalize_target_url(args.url),
        "active_tests": args.active_tests,
        "crawl_depth": args.crawl_depth,
        "auth_enabled": bool(auth_url and args.auth_user and args.auth_pass),
        "auth_url": auth_url,
        "auth_user": args.auth_user or "",
        "auth_pass": args.auth_pass or "",
    }
    config_data.update(config_updates)
    return config_data


def build_output_path(output_argument: Optional[str], report_format: str) -> Path:
    """Build the final report path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reports_dir = get_app_dir() / "reports"
    reports_dir.mkdir(exist_ok=True)

    if output_argument:
        output_file = Path(output_argument).resolve()
    else:
        output_file = reports_dir / f"scan_report_{timestamp}.{report_format}"

    output_file.parent.mkdir(parents=True, exist_ok=True)
    return output_file


async def run_scan(config: ScannerConfig):
    """Run the scan engine and return results."""
    scanner = Scanner(config)
    return await scanner.scan()


def run_scanner():
    """Main entry point for the scanner with enhanced CLI."""
    parser = argparse.ArgumentParser(
        prog="Web Security Scanner",
        description=(
            "Professional Web Application Security Scanner\n\n"
            "Performs reconnaissance, vulnerability assessment, and generates "
            "detailed security reports in HTML, JSON, or PDF formats."
        ),
        epilog=(
            "\nEXAMPLES:\n"
            "  Basic scan:\n"
            "    python main.py --url https://example.com\n\n"
            "  Comprehensive scan with active tests:\n"
            "    python main.py --url https://example.com --active-tests --format html\n\n"
            "  Authenticated scan:\n"
            "    python main.py --url https://app.local --auth-url /login \\\n"
            "      --auth-user admin --auth-pass secret123\n\n"
            "  Detailed debugging:\n"
            "    python main.py --url https://example.com --verbose --debug-auth\n\n"
            "IMPORTANT: Always obtain explicit written authorization before scanning "
            "any system you do not own."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Required arguments
    parser.add_argument(
        "--url",
        required=True,
        help="Target URL to scan (e.g., https://example.com)"
    )

    # Configuration
    parser.add_argument(
        "--config",
        help="Path to YAML configuration file for advanced settings"
    )
    
    # Scanning options
    parser.add_argument(
        "--active-tests",
        action="store_true",
        default=True,
        help="Enable active injection tests (XSS, SQLi, etc.) - requires authorization"
    )
    
    parser.add_argument(
        "--crawl-depth",
        type=int,
        default=3,
        metavar="DEPTH",
        help="Maximum crawling depth for link discovery (default: 3)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        metavar="SECONDS",
        help="Request timeout in seconds (default: 10)"
    )

    # Authentication options
    auth_group = parser.add_argument_group("Authentication", "Options for authenticated scanning")
    auth_group.add_argument(
        "--auth-url",
        help="Login/authentication URL for credential-based scanning"
    )
    auth_group.add_argument(
        "--auth-user",
        help="Username for authentication"
    )
    auth_group.add_argument(
        "--auth-pass",
        help="Password for authentication"
    )
    auth_group.add_argument(
        "--debug-auth",
        action="store_true",
        help="Enable detailed authentication debugging"
    )

    # Output options
    output_group = parser.add_argument_group("Output", "Report generation options")
    output_group.add_argument(
        "--format",
        choices=["html", "json", "pdf"],
        default="html",
        help="Report format (default: html)"
    )
    output_group.add_argument(
        "--output",
        help="Custom output path for report (default: reports/scan_report_<timestamp>.<format>)"
    )

    # Logging options
    log_group = parser.add_argument_group("Logging", "Logging and debug options")
    log_group.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging (DEBUG level)"
    )
    log_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output (ERROR level only)"
    )

    args = parser.parse_args()

    try:
        # Setup logging
        if args.quiet:
            setup_logging(False)
            logging.getLogger().setLevel(logging.ERROR)
        else:
            setup_logging(args.verbose)
        
        # Build configuration
        config_data = build_runtime_config(args)
        
        # Add timeout to config
        if args.timeout:
            config_data.timeout = args.timeout
        
        # Log scan initialization
        logging.info("=" * 70)
        logging.info("Security Assessment Initiated")
        logging.info("=" * 70)
        logging.info("Target: %s", args.url)
        logging.info("Active Tests: %s", "enabled" if args.active_tests else "disabled")
        if args.auth_url:
            logging.info("Authenticated Scanning: enabled")
        
        # Run scan
        results = asyncio.run(run_scan(config_data))

        if not results:
            logging.error("Scan completed with no results")
            return 1

        # Generate report
        output_file = build_output_path(args.output, args.format)
        generate_report(
            scan_results=results,
            output_format=args.format,
            output_file=str(output_file),
        )

        logging.info("=" * 70)
        logging.info("Security Assessment Report Generated")
        logging.info("=" * 70)
        logging.info("Report Location: %s", output_file)
        return 0
    
    except KeyboardInterrupt:
        logging.warning("\nScan interrupted by user")
        return 130
    except Exception as exc:
        logging.error("Scan failed: %s", str(exc), exc_info=args.verbose)
        if args.verbose:
            logging.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(run_scanner())
