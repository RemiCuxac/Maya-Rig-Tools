import json
import re
import os


# ------ OS

def read_file(path, json_type=False):
    with open(path) as f:
        if json_type:
            return json.load(f)
        else:
            return f.read()


import re
import os


class ShelfParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.proc_name = "shelf_Custom"
        self.global_strings = ["$gBuffStr", "$gBuffStr0", "$gBuffStr1"]
        self.items = []

        if os.path.exists(file_path):
            self._parse()

    @staticmethod
    def _clean_value(raw_val):
        val = raw_val.strip()
        # Handle complex MEL (Multiple quotes or code blocks)
        if val.count('"') > 2 or ('(' in val and ')' in val):
            return val
        # Handle standard strings
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1].replace('\\"', '"')
        # Handle Numbers/Lists
        if re.match(r'^-?[\d\.\s]+$', val):
            parts = val.split()
            try:
                nums = [float(x) if '.' in x else int(x) for x in parts]
                return nums if len(nums) > 1 else nums[0]
            except ValueError:
                return val
        return val

    def _parse(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        proc_match = re.search(r'global proc (\w+)', content)
        if proc_match:
            self.proc_name = proc_match.group(1)

        globals_found = re.findall(r'global string (.*?);', content)
        if globals_found:
            self.global_strings = [g.strip() for g in globals_found]

        # Match blocks: shelfButton or separator
        item_blocks = re.finditer(r'(\w+)\s+(.*?)\n\s*;\s*\n', content, re.DOTALL)

        self.items = []
        for match in item_blocks:
            cmd_type = match.group(1)
            if cmd_type in ['global', 'proc']: continue

            flags_list = []
            block_body = match.group(2)

            # CRITICAL FIX:
            # We look for a dash '-' only if it is preceded by a newline and whitespace.
            # This ignores '-d' or '-1' inside your single-line or multi-line strings.
            pattern = r'^\s*-(\w+)\s+(.*?)(?=\n\s*-\w+|$)'
            matches = re.findall(pattern, block_body, re.MULTILINE | re.DOTALL)

            for flag, raw_val in matches:
                flags_list.append((flag, self._clean_value(raw_val)))

            if flags_list:
                self.items.append({"_type": cmd_type, "flags": flags_list})

    def find_button_by_label(self, label):
        """Returns the first button dictionary matching the label."""
        for item in self.items:
            for key, value in item["flags"]:
                if key == "label" and value == label:
                    return item
        return None

    def update_button_flag(self, label, flag_to_update, new_value):
        """Updates a specific flag for a button identified by its label."""
        item = self.find_button_by_label(label)
        if item:
            for i, (flag, value) in enumerate(item["flags"]):
                if flag == flag_to_update:
                    item["flags"][i] = (flag_to_update, new_value)
                    return True
        return False

    def save(self, output_path=None):
        path = output_path or self.file_path

        # Header Setup
        lines = [f"global proc {self.proc_name} () {{"]
        lines += [f"    global string {gs};" for gs in self.global_strings] + [""]

        for item in self.items:
            lines.append(f"    {item['_type']}")
            for key, val in item["flags"]:
                if isinstance(val, list):
                    v = " ".join(map(str, val))
                elif isinstance(val, str):
                    # --- FIX START ---
                    # Remove accidental outer single quotes if they wrap the whole script
                    if len(val) >= 2 and val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    # --- FIX END ---

                    # If already MEL-formatted (quoted/complex), use as-is
                    if val.count('"') > 1 or "(" in val:
                        if val.startswith('"""'):
                            v = '"' + val[:].replace('"', '\\"').replace("\\'", "'") + '"'
                        else:
                            v = val
                    else:
                        # Escape backslashes, then quotes, then newlines
                        clean = val.replace('\n', '\\n')
                        v = f'"{clean}"'
                else:
                    v = str(val)

                lines.append(f"        -{key} {v}")
            lines.append("    ;\n")

        lines.append("}")

        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        print(f"Saved: {path}")