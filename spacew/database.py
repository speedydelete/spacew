
from __future__ import annotations

from typing import Any, Generator, Iterable

import re
import json
import os
from datetime import datetime, date, time


__all__ = ['Row', 'Database', 'strlist', 'intlist', 'timelist']


class DatabaseError(Exception):
    pass

RE_COMMA = re.compile(r'(?<!\\),')
RE_COMMA_REPL = re.compile(r'(?<!\\)\\,')

def comma_split(text: str) -> list[str]:
    items = RE_COMMA.split(text)
    items = [RE_COMMA_REPL.sub(',', item).replace('\\\\', '\\') for item in items]
    return items

def comma_join(items: Iterable[str]) -> str:
    items = [item.replace(',', '\\,').replace('\\\\', '\\') for item in items]
    return ','.join(items)

class strlist(list):
    pass
class intlist(list):
    pass
class timelist(list):
    pass

DATA_TYPES: dict[str, type] = {
    'bool': bool,
    'int': int,
    'float': float,
    'complex': complex,
    'str': str,
    'date': date,
    'time': time,
    'datetime': datetime,
    'strlist': strlist,
    'intlist': intlist,
    'timelist': timelist,
}

with open('meta_types.json', 'r', encoding='utf-8') as meta_types:
    META_TYPES = {k: eval(v) for k, v in json.load(meta_types).items()}

def to_field(data: Any) -> str:
    if data is None:
        return ''
    if isinstance(data, bool):
        return '1' if data else ''
    elif isinstance(data, int | float):
        return repr(data)
    elif isinstance(data, complex):
        return f'{data.real!r}+{data.imag!r}'
    elif isinstance(data, str):
        return data
    elif isinstance(data, date | time | datetime):
        return str(data)
    elif isinstance(data, list | tuple):
        if isinstance(data[0], str):
            try:
                return ','.join([item.replace('\\', '\\\\').replace(',', '\\,') for item in data])
            except AttributeError:
                raise ValueError('not all elements in strlist are strings') from None
        elif isinstance(data[0], int):
            try:
                return ','.join([repr(item) for item in data])
            except AttributeError:
                raise ValueError('not all elements in intlist are ints') from None
        elif isinstance(data[0], time):
            return ','.join([str(item) for item in data])
        else:
            raise ValueError(f'invalid type for list element: {type(data[0])!r}')
    else:
        raise ValueError(f'invalid field value: {data!r}')

def from_field(data: str, dtype: type) -> Any:
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
        return data
    elif dtype in (date, time, datetime):
        return dtype.fromisoformat(data)
    elif dtype == strlist:
        return [item.replace('\\,', ',').replace('\\\\', '\\') for item in RE_COMMA.split(data)]
    elif dtype == intlist:
        return [int(item) for item in RE_COMMA.split(data)]
    else:
        raise ValueError(f'invalid data type: {dtype!r}')


class Row:

    def __init__(self, db: Database, name: Any, fields: dict[str, Any]) -> None:
        self._db = db
        self.name = name
        self._fields = fields

    def __getattr__(self, attr: str) -> Any:
        print(self._fields)
        if attr in self._fields:
            return self._fields[attr]
        else:
            raise AttributeError(f'attribute not found: \'{attr}\'')

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr.startswith('_') or attr == 'name':
            self.__dict__[attr] = value
        elif attr in self._fields:
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
        self._db[self.name] = self

    def _to_field(self):
        return (to_field(self.name),) + tuple(to_field(field) for field in self._fields.values())


class Database:

    def __init__(self, filename: str, db_schema: dict[str, type] | None = None, \
                 fntype: type | None = None, **metadata: Any):
        self.filename = filename
        if db_schema is None:
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    data = [line[:-1] for line in file.readlines()]
            except FileNotFoundError:
                raise ValueError('schema required for creating new database') from None
            meta = [line.split('=') for line in data if line[0] == '#']
            meta = {line[0][1:]: '='.join(line[1:]) for line in meta}
            self.meta = {k: from_field(v, META_TYPES[k]) for k, v in meta.items()}
            try:
                schema = self.meta['schema']
                schema = [DATA_TYPES[dtype] for dtype in schema]
            except KeyError:
                raise DatabaseError(f'database {filename!r} has invalid or no schema') from None
            self.fntype, self.schema = schema[0], schema[1:]
            data = [tuple(comma_split(line)) for line in data if not line.startswith('#')]
            self.fields = data[0][1:]
            self.data = data[1:]
            self.names = [from_field(row[0], self.fntype) for row in self.data]
        else:
            if os.path.exists(self.filename):
                raise DatabaseError(f'database already exists: \'{self.filename}\'')
            self.fields = tuple(db_schema.keys())
            if fntype is None:
                raise TypeError('fntype required for creating new database')
            self.schema = (fntype,) + tuple(db_schema.values())
            self.fntype = fntype
            metadata['schema'] = ','.join([dtype.__name__ for dtype in self.schema])
            self.meta = metadata
            self.data = []
            self.names = []
    
    def __iter__(self) -> Generator[Row, None, None]:
        for name in self.names:
            yield self[name]

    def __len__(self):
        return len(self.names)

    def __getitem__(self, item) -> Row:
        if not isinstance(item, int):
            item = self.names.index(item)
        try:
            row = self.data[item]
            fields = {self.fields[i]: from_field(field, self.schema[i]) for i, field in enumerate(row[1:])}
            return Row(self, from_field(row[0], self.fntype), fields)
        except KeyError:
            raise ValueError(f'item {item!r} not in database') from None

    def __setitem__(self, item: Any, row: Row) -> None:
        if not isinstance(item, int):
            item = to_field(item)
            item = self.names.index(item)
        self.data[item] = row._to_field()

    def new_row(self, name: Any) -> Row:
        row = Row(self, name, {field: None for field in self.fields})
        self.data.append(row._to_field())
        self.names.append(to_field(name))
        return row
    
    def add_row(self, name: Any) -> Row:
        return self.new_row(name)

    def save(self):
        data = '\n'.join([comma_join(row) for row in self.data])
        data = 'name,' + ','.join(self.fields) + '\n' + data
        for k, v in self.meta.items():
            data = f'#{k}={v}\n' + data
        with open(self.filename, 'w', encoding='utf-8') as file:
            file.write(data)
