#! /usr/bin/env python3

import os
import sys
import subprocess
import yaml
import argparse
import urllib.request
import shutil
from pathlib import Path

RELEASES_FILE = 'releases.yml'
INSTALL_DIR = '/opt'
TMP_DIR = '/tmp'

# Load release data from releases.yml
with open(RELEASES_FILE, 'r') as f:
    releases = yaml.safe_load(f)['toolchains']


def list_versions(installed_only=False):
    installed_versions = get_installed_versions()
    print("Available versions (* = installed):")
    for version in releases.keys():
        is_installed = version in installed_versions
        if installed_only and not is_installed:
            continue
        print(f"{'* ' if is_installed else ''}{version}")


def get_installed_versions():
    installed_versions = []
    for version in releases.keys():
        package_name = f"{releases[version]['package']}-{version}"
        install_path = Path(INSTALL_DIR) / package_name
        if install_path.exists():
            installed_versions.append(version)
    return installed_versions


def install_version(version):
    if version not in releases:
        print(f"Error: Version '{version}' not found.")
        sys.exit(1)

    # Check if the version is already installed
    installed_versions = get_installed_versions()
    if version in installed_versions:
        print(f"Version '{version}' is already installed.")
        return

    # Get the architecture of the system
    arch = os.uname().machine
    if arch not in releases[version]['archs']:
        print(f"Error: Version '{version}' is not available for architecture '{arch}'.")
        sys.exit(1)

    # Download the package
    package_name = f"{releases[version]['package']}-{version}"
    url = releases[version]['link'].replace('${arch}', arch)
    archive_path = Path(TMP_DIR) / f"{package_name}.tar.xz"

    print(f"Downloading {package_name} from {url}...")
    if (not archive_path.exists()):
        urllib.request.urlretrieve(url, archive_path)
    else:
        print(f"Found cached {archive_path}")

    # Extract the package to /opt
    install_path = Path(INSTALL_DIR) / package_name
    subprocess.run(["sudo", "mkdir", "-p", install_path], check=True)
    print(f"Installing {package_name} to {install_path}...")
    try:
        subprocess.run(['sudo', 'tar', '-xf', archive_path, '-C', install_path, '--strip-components=1'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to extract {package_name}: {e}")
        sys.exit(1)
    finally:
        # Clean up the archive
        archive_path.unlink()

    # Register the toolchain with update-alternatives
    register_version(install_path, releases[version]['build_date'])

    print(f"Version '{version}' installed successfully.")

def register_version(install_path, priority):

    command = ["sudo", "update-alternatives", "--verbose", "--install", "/usr/bin/arm-none-eabi-gcc", install_path / "bin" / "arm-none-eabi-gcc", priority]

    tools = ['strings', 'gcc-ranlib', 'gcov-dump', 'ld', 'cpp', 'strip', 'readelf', 'objdump', 'c++filt', 'gprof', 'gdb-add-index-py', 'c++', 'gdb-add-index', 'gcov', 'as', 'gdb', 'ranlib', 'gcc-nm', 'elfedit', 'gcov-tool', 'gcc-ar', 'ar', 'objcopy', 'addr2line', 'gdb-py', 'ld.bfd', 'g++', 'size', 'nm']

    for tool in tools:
        binary_name = f"arm-none-eabi-{tool}"
        command.extend(["--slave", f"/usr/bin/{binary_name}", binary_name, install_path / "bin" / binary_name])

    subprocess.run(command, check=True)


def use_version(version):
    if version not in releases:
        print(f"Error: Version '{version}' not found.")
        sys.exit(1)

    installed_versions = get_installed_versions()
    if version not in installed_versions:
        print(f"Error: Version '{version}' is not installed.")
        sys.exit(1)

    priority = releases[version]['build_date']
    subprocess.run(['sudo', 'update-alternatives', '--set', 'arm-none-eabi-gcc', f"/opt/{releases[version]['package']}-{version}/bin/arm-none-eabi-gcc"], check=True)
    print(f"Using version '{version}' as the default.")


def main():
    parser = argparse.ArgumentParser(description='Manage GNU ARM toolchain versions.')
    subparsers = parser.add_subparsers(dest='command')

    # List versions command
    list_parser = subparsers.add_parser('list', help='List available versions.')
    list_parser.add_argument('versions', nargs='?', default='versions', help='List versions.')
    list_parser.add_argument('--installed', action='store_true', help='List only installed versions.')

    # Install version command
    install_parser = subparsers.add_parser('install', help='Install a specified version.')
    install_parser.add_argument('version', help='Version to install.')

    # Use version command
    use_parser = subparsers.add_parser('use', help='Select a version to use.')
    use_parser.add_argument('version', help='Version to use.')

    args = parser.parse_args()

    if args.command == 'list':
        list_versions(installed_only=args.installed)
    elif args.command == 'install':
        install_version(args.version)
    elif args.command == 'use':
        use_version(args.version)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
