#!/usr/bin/env python3
"""Fix compile_commands.json to include missing include paths.

This script adds:
1. Workspace root to include paths (for #include "shardy/..." style includes)
2. Bazel output paths for generated headers (for SDY-related files)
"""

import json
import os
import subprocess
import sys


def get_workspace_root():
    """Get the workspace root directory."""
    return os.path.abspath('.')


def get_bazel_execroot():
    """Get the bazel execroot directory."""
    try:
        result = subprocess.run(
            ['bazel', 'info', 'execution_root'],
            capture_output=True,
            text=True,
            cwd=get_workspace_root()
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def fix_compile_commands(compile_commands_path='compile_commands.json'):
    """Fix compile_commands.json by adding missing include paths."""
    if not os.path.exists(compile_commands_path):
        print(f"Error: {compile_commands_path} not found", file=sys.stderr)
        return 1

    # Read compile_commands.json
    with open(compile_commands_path, 'r') as f:
        data = json.load(f)

    workspace_root = get_workspace_root()
    execroot = get_bazel_execroot()
    
    workspace_flag = f'-I{workspace_root}'
    modified_count = 0
    bazel_out_added = 0

    for entry in data:
        args = entry.get('arguments', [])
        file_path = entry.get('file', '')
        
        # Add workspace root if not present
        if workspace_flag not in args:
            # Find where to insert (after compiler, before source file)
            insert_pos = 1
            for i, arg in enumerate(args):
                if arg.endswith(('.cc', '.cpp', '.c', '.cxx')):
                    insert_pos = i
                    break
            args.insert(insert_pos, workspace_flag)
            entry['arguments'] = args
            modified_count += 1

        # Add bazel-out base path for files that need generated headers
        # This is needed for files that include generated .inc files from gentbl_cc_library
        if execroot and ('sdy' in file_path.lower() or 'shardy' in file_path.lower() or 
                         'passes.h.inc' in file_path or '.inc' in file_path):
            # Add both relative (for compatibility) and absolute paths
            bazel_out_base_abs = os.path.join(execroot, 'bazel-out', 'k8-fastbuild', 'bin')
            bazel_out_base_rel = 'bazel-out/k8-fastbuild/bin'
            
            # Check if the relative path flag is already present (exact match)
            has_rel_flag = f'-I{bazel_out_base_rel}' in args
            
            # Add relative path (works from workspace root where IDEs typically run)
            # The relative path allows finding files like passes.h.inc at:
            # bazel-out/k8-fastbuild/bin/shardy/dialect/sdy/transforms/export/passes.h.inc
            if not has_rel_flag:
                try:
                    workspace_idx = next(i for i, a in enumerate(args) if workspace_root in a)
                    # Add relative path that works from workspace root
                    bazel_out_flag = f'-I{bazel_out_base_rel}'
                    args.insert(workspace_idx + 1, bazel_out_flag)
                    entry['arguments'] = args
                    bazel_out_added += 1
                except StopIteration:
                    # If workspace root not found, add after first -I flag
                    for i, arg in enumerate(args):
                        if arg.startswith('-I'):
                            args.insert(i + 1, f'-I{bazel_out_base_rel}')
                            entry['arguments'] = args
                            bazel_out_added += 1
                            break

    # Write back
    with open(compile_commands_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Fixed {compile_commands_path}:")
    print(f"  - Added workspace root include path to {modified_count} entries")
    if bazel_out_added > 0:
        print(f"  - Added bazel-out include paths to {bazel_out_added} SDY-related entries")
    
    return 0


if __name__ == '__main__':
    sys.exit(fix_compile_commands())

