
from __future__ import annotations

from typing import Any

import re
import json
import os
from datetime import datetime, date, time


__all__ = ['Row', 'Database']


class DatabaseError(Exception):
    pass


RE_COMMA = re.compile(r'(?<!\\),')
BASE_DTYPE = r'bool|int|float|complex|str|date|time|datetime'
RE_DTYPE = re.compile('bool|')


DATA_TYPES: dict[str, type] = {
    'bool': bool,
    'int': int,
    'float': float,
    'complex': complex,
    'str': str,
    'date': date,
    'time': time,
    'datetime': datetime,
}

with open('meta_types.json', 'r', encoding='utf-8') as meta_types:
    META_TYPES = json.load(meta_types)

def str_field(data: Any) -> str:
    if data is None:
        return ''
    if isinstance(data, bool):
        return '1' if data else ''
    elif isinstance(data, int | float):
        return repr(data)
    elif isinstance(data, complex):
        return f'{data.real!r}+{data.imag!r}'
    elif isinstance(data, str):
        return data.replace('\\', '\\\\').replace(',', '\\,')
    elif isinstance(data, date | time | datetime):
        return str(data)
    else:
        raise ValueError(f'invalid field value: {data!r}')

def parse_field(data: str, dtype: type) -> Any:
    if data == '':
        return None
    if dtype == bool:
        return len(data) > 0
    elif dtype == int:
        return int(float(data))
    elif dtype == float:
        return float(data)
    elif dtype == complex:
        real, imag = data.split('+')
        return complex(float(real), float(imag))
    elif dtype == str:
        return data.replace('\\,', ',').replace('\\\\', '\\')
    elif dtype in (date, time, datetime):
        return dtype.fromisoformat(data)
    else:
        raise ValueError(f'invalid data type: {dtype!r}')

class Row:

    def __init__(self, db: Database, name: str, fields: dict[str, Any]) -> None:
        self.db = db
        self.name = name
        self._fields = fields

    def __getattr__(self, attr: str) -> Any:
        if attr in self._fields:
            return self._fields[attr]
        else:
            raise AttributeError(f'attribute not found: \'{attr}\'')

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in self._fields:
            self._fields[attr] = value
        else:
            self.__dict__[attr] = value

    def __getitem__(self, item: str) -> Any:
        if item in self._fields:
            return self._fields[item]
        else:
            raise KeyError(f'field not found: \'{item}\'')

    def __setitem__(self, item: str, value: Any) -> None:
        if item in self._fields:
            self._fields[item] = value
        else:
            raise KeyError(f'field not found: \'{item}\'')

    def save(self):
        self.db[self.name] = self


class Database:

    def __init__(self, filename: str, db_schema: dict[str, type] | None = None, **metadata: Any):
        self.filename = filename
        if db_schema is None:
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = file.readlines()
            except FileNotFoundError:
                raise ValueError('cannot create new database without schema') from None
            meta = [line.split('=') for line in data if line[0] != '#']
            meta = {line[0]: '='.join(line[1]) for line in meta}
            self.meta = {k: parse_field(v, META_TYPES[k]) for k, v in meta.items()}
            try:
                schema = self.meta['schema'].split(',')
                schema = [DATA_TYPES[dtype] for dtype in schema]
            except KeyError:
                raise DatabaseError(f'database {filename!r} has invalid or no schema') from None
            self.fntype, self.schema = schema[0], schema[1:]
            data = [tuple(RE_COMMA.split(line)) for line in data]
            self.fields = data[0][1:]
            self.data = data
            self.names = [row[0] for row in data]
        else:
            if os.path.exists(self.filename):
                raise DatabaseError(f'database already exists: \'{self.filename}\'')
            self.fields = tuple(db_schema.keys())
            self.schema = tuple(db_schema.values())
            self.meta = metadata

    def __getitem__(self, item: str | int) -> Row:
        if isinstance(item, str):
            item = self.names.index(item)
        try:
            row = self.data[item]
            fields = {self.fields[i]: parse_field(field, self.schema[i]) for i, field in enumerate(row[1:])}
            return Row(self, parse_field(row[0], self.fntype), fields)
        except KeyError:
            raise ValueError(f'item {item!r} not in database') from None

    def __setitem__(self, item: str | int, value: Row) -> None:
        if isinstance(item, str):
            item = self.names.index(item)
        self.data[item] = tuple(str_field(field) for field in value._fields.values())

    def new_row(self, name):
        return Row(self, name, {field: None for field in self.fields})

    def save(self):
        data = '\n'.join([','.join(row) for row in self.data])
        data = str(self.fntype) + ',' + ','.join(self.fields) + '\n' + data
        for k, v in self.meta.items():
            data = f'#{k}={v}\n' + data
        with open(self.filename, 'w', encoding='utf-8') as file:
            file.write(data)
