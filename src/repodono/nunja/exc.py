try:
    from builtins import FileNotFoundError
except ImportError:
    class FileNotFoundError(OSError):
        pass


class TemplateNotFoundError(FileNotFoundError):
    pass
