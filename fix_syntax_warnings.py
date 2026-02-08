#!/usr/bin/env python3
# Fix SyntaxWarnings in Odoo core files

import os
import re

fixes = [
    {
        'file': r'C:\odoo14c\server\odoo\tools\appdirs.py',
        'line': 178,
        'old': '  """Return full path to the user-shared data dir for this application.',
        'new': '  r"""Return full path to the user-shared data dir for this application.',
        'description': 'Add raw string prefix to docstring with \\P'
    },
    {
        'file': r'C:\odoo14c\server\odoo\tools\translate.py',
        'line': 858,
        'old': "  string_list = [s.replace('\\n', ' ').strip() for s in re.split('\\[\\[.+?\\]\\]', m.text)]",
        'new': r"  string_list = [s.replace('\n', ' ').strip() for s in re.split(r'\[\[.+?\]\]', m.text)]",
        'description': 'Use raw string for regex pattern with \\['
    },
    {
        'file': r'C:\odoo14c\server\odoo\tools\sql.py',
        'line': 248,
        'old': "  return to_escape.replace('\\\\', r'\\\\').replace('%', '\\%').replace('_', '\\_')",
        'new': r"  return to_escape.replace('\\', r'\\').replace('%', r'\%').replace('_', r'\_')",
        'description': 'Use raw strings for escape sequences'
    },
    {
        'file': r'C:\odoo14c\server\odoo\tools\mail.py',
        'line': 344,
        'old': "  html = re.sub('<br\\s*/?>', '\\n', html)",
        'new': r"  html = re.sub(r'<br\s*/?>', '\n', html)",
        'description': 'Use raw string for regex pattern with \\s'
    }
]

print("="*70)
print("FIXING ODOO SYNTAX WARNINGS")
print("="*70)

for i, fix in enumerate(fixes, 1):
    print(f"\n{i}. {fix['description']}")
    print(f"   File: {fix['file']}")
    print(f"   Line: {fix['line']}")
    
    if os.path.exists(fix['file']):
        # Read file
        with open(fix['file'], 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if line needs fixing
        line_index = fix['line'] - 1
        if line_index < len(lines):
            current_line = lines[line_index].rstrip('\n')
            
            # For the first fix, just check if it starts with the expected pattern
            if 'appdirs.py' in fix['file']:
                if '"""Return full path' in current_line and not current_line.strip().startswith('r"""'):
                    lines[line_index] = current_line.replace('  """Return', '  r"""Return') + '\n'
                    print(f"   ✓ Fixed")
                else:
                    print(f"   ⊗ Already fixed or pattern not found")
            else:
                # For other fixes, we need to find and replace
                # Let's search nearby lines
                found = False
                for offset in range(-2, 3):
                    check_index = line_index + offset
                    if 0 <= check_index < len(lines):
                        if 'string_list = ' in fix['old'] and 'string_list = ' in lines[check_index]:
                            if "re.split('\\[" in lines[check_index]:
                                lines[check_index] = lines[check_index].replace(
                                    "re.split('\\[\\[.+?\\]\\]'",
                                    r"re.split(r'\[\[.+?\]\]'"
                                )
                                found = True
                                print(f"   ✓ Fixed (at line {check_index + 1})")
                                break
                        elif 'to_escape.replace' in fix['old'] and 'to_escape.replace' in lines[check_index]:
                            if "'\\%'" in lines[check_index] or "'\\_'" in lines[check_index]:
                                lines[check_index] = lines[check_index].replace(
                                    "'\\%'", r"r'\%'"
                                ).replace(
                                    "'\\_'", r"r'\_'"
                                )
                                found = True
                                print(f"   ✓ Fixed (at line {check_index + 1})")
                                break
                        elif 're.sub(' in fix['old'] and 're.sub(' in lines[check_index]:
                            if "'<br\\s" in lines[check_index]:
                                lines[check_index] = lines[check_index].replace(
                                    "'<br\\s*/?>'",
                                    r"r'<br\s*/?>'"
                                )
                                found = True
                                print(f"   ✓ Fixed (at line {check_index + 1})")
                                break
                
                if not found:
                    print(f"   ⊗ Pattern not found near line {fix['line']}")
        
        # Write file back
        with open(fix['file'], 'w', encoding='utf-8') as f:
            f.writelines(lines)
    else:
        print(f"   ✗ File not found!")

print("\n" + "="*70)
print("FIX COMPLETE")
print("="*70)
print("\nRestart Odoo to see the warnings disappear.")
