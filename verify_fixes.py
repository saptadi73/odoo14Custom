#!/usr/bin/env python3
# Verify the fixes

import re

files_to_check = [
    ('C:\\odoo14c\\server\\odoo\\tools\\appdirs.py', 178, r'r"""', 'Raw string prefix'),
    ('C:\\odoo14c\\server\\odoo\\tools\\translate.py', 858, r"r'\[", 'Raw regex pattern'),
    ('C:\\odoo14c\\server\\odoo\\tools\\sql.py', 248, r"r'\%'", 'Raw escape for %'),
    ('C:\\odoo14c\\server\\odoo\\tools\\mail.py', 344, r"r'<br\s", 'Raw regex pattern'),
]

print("="*70)
print("VERIFICATION OF FIXES")
print("="*70)

for filepath, line_num, pattern, desc in files_to_check:
    print(f"\n{desc}:")
    print(f"  File: {filepath}")
    print(f"  Line: {line_num}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if line_num - 1 < len(lines):
            line_content = lines[line_num - 1].rstrip()
            print(f"  Content: {line_content[:80]}...")
            
            if pattern in line_content:
                print(f"  ✓ VERIFIED - Contains '{pattern}'")
            else:
                # Check nearby lines
                found = False
                for offset in range(-2, 3):
                    check_line = line_num - 1 + offset
                    if 0 <= check_line < len(lines) and pattern in lines[check_line]:
                        print(f"  ✓ VERIFIED - Found at line {check_line + 1}")
                        found = True
                        break
                if not found:
                    print(f"  ⚠ Pattern '{pattern}' not found")
        else:
            print(f"  ✗ Line number out of range")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
