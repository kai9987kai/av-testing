import argparse
import io
import os
import platform
import sys
import textwrap
import time
import urllib.error
import urllib.request
import webbrowser
import zipfile
from pathlib import Path


def build_eicar_string() -> str:
    # Built from fragments so the source file does not contain the full signature inline.
    parts = [
        "X5O!P%@AP[4\\PZX54(P^)7CC)7}$",
        "EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
        "!$H+H*",
    ]
    return "".join(parts)


def write_eicar_file(output_path: Path, overwrite: bool) -> int:
    if output_path.exists() and not overwrite:
        print(f"[skip] File already exists: {output_path}")
        print("Use --overwrite to replace it.")
        return 1

    payload = build_eicar_string().encode("ascii")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(payload)

    print(f"[ok] Wrote EICAR test file: {output_path}")
    print("If your AV is active, it may quarantine this file immediately.")
    return 0


def write_zip_file(output_path: Path, entries: dict[str, bytes], overwrite: bool) -> int:
    if output_path.exists() and not overwrite:
        print(f"[skip] File already exists: {output_path}")
        print("Use --overwrite to replace it.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries.items():
            zf.writestr(name, data)

    print(f"[ok] Wrote ZIP test file: {output_path}")
    print("If your AV is active, it may quarantine this file immediately.")
    return 0


def write_eicar_test_set(output_dir: Path, overwrite: bool) -> int:
    payload = build_eicar_string().encode("ascii")
    output_dir.mkdir(parents=True, exist_ok=True)

    exit_code = 0
    exit_code = max(exit_code, write_eicar_file(output_dir / "eicar.com", overwrite=overwrite))
    exit_code = max(exit_code, write_eicar_file(output_dir / "eicar.com.txt", overwrite=overwrite))
    exit_code = max(
        exit_code,
        write_zip_file(
            output_dir / "eicar_com.zip",
            {"eicar.com": payload},
            overwrite=overwrite,
        ),
    )

    inner_zip_buf = io.BytesIO()
    with zipfile.ZipFile(inner_zip_buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("eicar.com", payload)

    exit_code = max(
        exit_code,
        write_zip_file(
            output_dir / "eicarcom2.zip",
            {"eicar_com.zip": inner_zip_buf.getvalue()},
            overwrite=overwrite,
        ),
    )

    print(f"[info] EICAR test set written to: {output_dir.resolve()}")
    return exit_code


def system_report() -> None:
    print("[info] Safe AV test harness")
    print(f"[info] Platform: {platform.platform()}")
    print(f"[info] Python:   {platform.python_version()} ({sys.executable})")
    print(f"[info] Cores:    {os.cpu_count()}")
    print(f"[info] Time:     {time.strftime('%Y-%m-%d %H:%M:%S')}")


def open_amtso_checks() -> None:
    # AMTSO hosts safe test pages/files for validating endpoint/browser protections.
    urls = [
        "https://www.amtso.org/security-features-check/",
        "https://www.amtso.org/check-desktop-phishing-page/",
        "https://www.amtso.org/check-cloud-look-up/",
    ]
    print("[info] Opening AMTSO checks in your default browser:")
    for url in urls:
        print(f"  - {url}")
        webbrowser.open(url, new=2)


def download_to_file(url: str, output_path: Path, overwrite: bool) -> int:
    if output_path.exists() and not overwrite:
        print(f"[skip] File already exists: {output_path}")
        print("Use --overwrite to replace it.")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            data = response.read()
    except urllib.error.URLError as exc:
        print(f"[error] Failed to download {url}: {exc}")
        return 2

    with output_path.open("wb") as f:
        f.write(data)
    print(f"[ok] Downloaded {len(data)} bytes to {output_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safe antivirus test harness (EICAR/AMTSO). Default launch writes the EICAR test set.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python safe_av_test_harness.py
              python safe_av_test_harness.py --report
              python safe_av_test_harness.py --write-eicar
              python safe_av_test_harness.py --write-eicar-set
              python safe_av_test_harness.py --write-eicar-set test --overwrite
              python safe_av_test_harness.py --write-eicar test\\eicar.com.txt --overwrite
              python safe_av_test_harness.py --open-amtso
              python safe_av_test_harness.py --download-url https://example.com/file.bin out\\file.bin
            """
        ),
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Print a local environment report (harmless).",
    )
    parser.add_argument(
        "--write-eicar",
        nargs="?",
        const="eicar.com.txt",
        metavar="PATH",
        help="Write the standard EICAR AV test file (default: eicar.com.txt).",
    )
    parser.add_argument(
        "--write-eicar-set",
        nargs="?",
        const=".",
        metavar="DIR",
        help="Write common EICAR test variants (plain/txt/zip/double-zip) to DIR (default: current directory).",
    )
    parser.add_argument(
        "--open-amtso",
        action="store_true",
        help="Open official AMTSO security feature check pages in your browser.",
    )
    parser.add_argument(
        "--download-url",
        nargs=2,
        metavar=("URL", "PATH"),
        help="Download a file to PATH (for safe test files you control).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting output files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Default behavior writes the standard EICAR file for safe AV verification.
    if not any([args.report, args.write_eicar, args.write_eicar_set, args.open_amtso, args.download_url]):
        system_report()
        print("\n[info] No action selected. Writing default EICAR test set to current directory")
        return write_eicar_test_set(Path("."), overwrite=True)

    exit_code = 0

    if args.report:
        system_report()

    if args.write_eicar:
        result = write_eicar_file(Path(args.write_eicar), overwrite=args.overwrite)
        exit_code = max(exit_code, result)

    if args.write_eicar_set:
        result = write_eicar_test_set(Path(args.write_eicar_set), overwrite=args.overwrite)
        exit_code = max(exit_code, result)

    if args.open_amtso:
        open_amtso_checks()

    if args.download_url:
        url, path_str = args.download_url
        result = download_to_file(url, Path(path_str), overwrite=args.overwrite)
        exit_code = max(exit_code, result)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
