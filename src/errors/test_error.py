class TestException(Exception):
    def __init__(self, message="Test exception occurred"):
        self.message = message
        super().__init__(self.message)

class TestExceptionOne(Exception):
    def __init__(self, message="Test exception occurred"):
        self.message = message
        super().__init__(self.message)