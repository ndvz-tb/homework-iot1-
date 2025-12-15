import logging
import os


class FileNotFound(Exception):
    """
    Custom exception raised when the file does not exist
    during TextFileHandler object creation.
    """
    pass


class FileCorrupted(Exception):
    """
    Custom exception raised when file reading,
    writing or appending fails.
    """
    pass


def logged(exception, mode="console"):
    """
    Decorator for exception logging.

    exception: exception type to be logged
    mode: logging mode ("console" or "file")
    """

    def decorator(func):
        """
        Decorator that wraps the target function.
        """

        def wrapper(*args, **kwargs):
            """
            Wrapper that executes the function
            and logs the specified exception.
            """
            try:
                return func(*args, **kwargs)
            except exception as e:
                logger = logging.getLogger(func.__name__)
                logger.setLevel(logging.ERROR)

                if mode == "file":
                    handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
                else:
                    handler = logging.StreamHandler()

                formatter = logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                logger.addHandler(handler)

                logger.error(str(e))

                logger.removeHandler(handler)
                raise e

        return wrapper

    return decorator


class TextFileHandler:
    """
    Class for working with a text file.
    Provides reading, writing and appending
    with exception logging.
    """

    def __init__(self, path: str):
        """
        Initializes the object and checks
        if the file exists.
        """
        self.path = path

        if not os.path.exists(path):
            raise FileNotFound(f"File '{path}' does not exist!")


    @logged(FileCorrupted, mode="file")
    def read(self):
        """
        Reads and returns file content.
        """
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            raise FileCorrupted("Unable to read the file!")


    @logged(FileCorrupted, mode="console")
    def write(self, text: str):
        """
        Overwrites file content.
        """
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            raise FileCorrupted("Unable to write to the file!")


    @logged(FileCorrupted, mode="file")
    def append(self, text: str):
        """
        Appends text to the file.
        """
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            raise FileCorrupted("Unable to append to the file!")


if __name__ == "__main__":
    """
    Program entry point.
    """

    file_path = "data_corrupted.txt"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("test")

        handler = TextFileHandler(file_path)

        handler.path = "/invalid/path/to/force/error.txt"

        print("Attempting to read the file. Error and file logging expected.")

        handler.read()

    except FileNotFound as e:
        print(f"[{type(e).__name__}] {e}")

    except FileCorrupted as e:
        print(f"[{type(e).__name__}] {e}")

    if os.path.exists("log.txt"):
        print("The file 'log.txt' was successfully created.")
        with open("log.txt", "r", encoding="utf-8") as f:
            print("--- log.txt content ---")
            print(f.read())
            print("-----------------------")
    else:
        print("The file 'log.txt' was not created.")
