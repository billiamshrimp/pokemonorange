defeated_trainers = set()
collected_items = set()

def clear_all_flags():
    defeated_trainers.clear()

def get_defeated_trainers():
    return defeated_trainers

def defeat_trainer(name):
    defeated_trainers.add(name)

def get_collected_items():
    return collected_items

def collect_item(item_id):
    collected_items.add(item_id)