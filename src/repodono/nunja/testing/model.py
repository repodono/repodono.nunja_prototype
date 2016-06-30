# -*- coding: utf-8 -*-
"""
Generic dummy modules.
"""


class DummyTableData(object):
    """
    This is a data provider that feeds stuff to the table mold.
    """

    def __init__(self, columns, data, css=None):
        self.columns = columns
        self.data = data
        self.css = css or {}

    def to_jsonable(self):
        """
        Convert to a dict that can be dumped into json.
        """

        column_ids = [c[0] for c in self.columns]

        results = {
            "active_columns": [id_ for id_, name in self.columns],
            "column_map": dict(self.columns),
            "data": [
                dict(zip(column_ids, datum)) for datum in self.data
            ],
            "css": self.css,
        }

        return results


