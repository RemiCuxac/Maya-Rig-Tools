from pathlib import Path
from modules import python_utils as utils


shelf_path = Path(__file__).parent.parent / "shelf_Rigging_Custom.mel"
script_data_path = Path(__file__).parent / "script_data.json"

parsed_shelf = utils.ShelfParser(shelf_path)
json_data = utils.read_file(script_data_path, True)
for script, data in json_data.items():
    python_path = Path(__file__).parent.parent.parent / Path(script)
    python_data = repr(utils.read_file(python_path))
    parsed_shelf.update_button_flag(data["label"], "command", python_data)

parsed_shelf.save()