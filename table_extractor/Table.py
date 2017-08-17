# coding=utf-8


class Table:
    """
    Table class is a support class used by a Parser to manage a table.
    It collects table statistics and method to work over a table structure
    """

    def __init__(self):

        self.n_rows = 0
        self.n_cells = 0
        self.n_headers = 0
        self.cells_refined = 0
        self.data_refined_rows = 0

        self.table_section = None

        self.table_class = []
        self.table_attributes = {}

        self.headers = []
        self.headers_refined = []
        self.sub_headers = []
        self.data = []
        self.data_refined = []

        self.data_filtered = []

        # used for understanding if headers are in rows or in columns
        self.vertical_table = 0

    def count_data_cells_and_rows(self):
        """
        Method which set number of data cells and rows for this table

        :return:
        """
        data_num = 0
        rows = len(self.data_refined)
        # i don't want to count empty cell (empty cell has "-") --> no data in there
        for row in self.data_refined:
            keys = row.keys()
            for key in keys:
                # row[key] is a list
                if row[key][0] != "-":
                    data_num += 1
        self.cells_refined += data_num
        self.data_refined_rows += rows
        self.n_headers = len(self.headers_refined)
