class ColumnNameDoesNotExists(Exception):
    def __init__(self, column_name) -> None:
        super().__init__(self)
        self.column_name = column_name
    
    def __str__(self) -> str:
        return """%s is not an existing data column""" % (self.column_name)
    
    