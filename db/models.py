from pony import orm
from pony.orm import select

db = orm.Database()

class Character(db.Entity):
    _table_ = "characters"
    id = orm.PrimaryKey(str, 255)
    name = orm.Required(str, 255)
    prompt = orm.Required(orm.LongStr)

def init_models(host, user, passwd, dbName):
    db.bind(provider='mysql', host=host, user=user, passwd=passwd, db=dbName)
    db.generate_mapping(create_tables=False)

@orm.db_session
def get_character_name(id) -> str:
    return Character.get(id=id).name

@orm.db_session
def get_character_prompt(id):
    return Character.get(id=id).prompt

@orm.db_session
def get_character_prompt_by_name(name):
    return Character.get(name=name).prompt


