from alembic import context, op
from sqlalchemy.orm import sessionmaker

def get_engine_name():
    return op.get_bind().engine.name

def get_enable_disable_fk_command(enable: bool):
    if is_mysql():
        value = 1 if enable else 0
        return f'SET foreign_key_checks = {value};'
    elif is_psql():
        value = 'IMMEDIATE' if enable else 'DEFERRED'
        return f'SET CONSTRAINTS ALL {value};'
    elif is_sqlite():
        value = 'ON' if enable else 'OFF'
        return f'PRAGMA foreign_keys = {value}';

def is_sqlite():
    return get_engine_name() == 'sqlite'

def is_mysql():
    return get_engine_name() == 'mysql'

def is_psql():
    return get_engine_name() == 'postgresql'

def get_psql_enum_alter_commands(tables: list, columns: list, name: str, 
                                 values: list, default: str) -> list:
    formated_values = ','.join([f"'{x}'" for x in values])
    result = [
           f'ALTER TYPE "{name}" RENAME TO "{name}Old"',
           f'CREATE TYPE "{name}" AS ENUM({formated_values})']

    for table, column in zip(tables, columns):
        result.append(f'ALTER TABLE {table} RENAME COLUMN {column} to {column}_old')
        result.append(f"ALTER TABLE {table} ADD {column} \"{name}\" NOT NULL DEFAULT '{default}'")
        result.append(f"UPDATE {table} SET {column} = {column}_old::text::\"{name}\"")
        result.append(f"ALTER TABLE {table} DROP COLUMN {column}_old")
    result.append(f'DROP TYPE "{name}Old"')

    return result


def upgrade_actions(all_commands):
    ctx = context.get_context()
    session = sessionmaker(bind=ctx.bind)()
    connection = session.connection()

    try:
        for cmd in all_commands:
            if isinstance(cmd[0], str):
                connection.execute(cmd[0])
            elif isinstance(cmd[0], list):
                for row in cmd[0]:
                    connection.execute(row)
            else:
                cmd[0]()
    except:
        session.rollback()
        raise
    session.commit()


def downgrade_actions(all_commands):
    ctx = context.get_context()
    session = sessionmaker(bind=ctx.bind)()
    connection = session.connection()
    connection.execute(get_enable_disable_fk_command(False))

    try:
        for cmd in reversed(all_commands):
            if isinstance(cmd[1], str):
                connection.execute(cmd[1])
            elif isinstance(cmd[1], list):
                for row in cmd[1]:
                    connection.execute(row)
            else:
                cmd[1]()
    except:
        session.rollback()
        raise
    connection.execute(get_enable_disable_fk_command(True))
    session.commit()
