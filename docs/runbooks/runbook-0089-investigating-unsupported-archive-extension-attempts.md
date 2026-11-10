# RUNBOOK-0089: Investigating Unsupported Archive Extension Attempts

## Purpose
Review rejected uploads featuring unsupported file formats (e.g. `.rar`, `.7z`, executable binaries).

## Steps
1. Review server 400 error logs for `invalid_format`.
2. Confirm file header using `file <path>` utility.
3. Instruct user to convert to standard `.zip` or `.tar.gz` archive.
