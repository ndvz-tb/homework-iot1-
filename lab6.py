import logging
import os


class FileNotFound(Exception):
    """
    Власний виняток, який використовується у випадку,
    якщо файл не існує під час створення об'єкта класу.
    """
    pass


class FileCorrupted(Exception):
    """
    Власний виняток, який використовується у випадку,
    якщо виникають проблеми з читанням, записом або доступом до файлу.
    """
    pass


def logged(exception, mode="console"):
    """
    Декоратор для логування винятків.

    exception — тип винятку, який необхідно логувати.
    mode — режим логування: 'console' або 'file'.
    """

    def decorator(func):
        """
        Внутрішній декоратор, який приймає функцію та повертає обгорнуту версію.
        """

        def wrapper(*args, **kwargs):
            """
            Обгортка для виклику функції.
            Виконує функцію та перехоплює заданий виняток для логування.
            """
            try:
                return func(*args, **kwargs)
            except exception as e:
                logger = logging.getLogger(func.__name__)
                logger.setLevel(logging.ERROR)

                if mode == "file":
                    handler = logging.FileHandler("log.txt", mode="a", encoding="utf-8")
                else: handler = logging.StreamHandler

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
    Клас для роботи з текстовим файлом.
    Забезпечує читання, запис та дописування з логуванням помилок.
    """

    def __init__(self, path: str):
        """
        Конструктор класу.
        Приймає шлях до файлу та перевіряє його існування.
        Якщо файл не існує — генерується виняток FileNotFound.
        """
        self.path = path

        if not os.path.exists(path):
            raise FileNotFound(f"Файл '{path}' не існує!")


    @logged(FileCorrupted, mode="file")
    def read(self):
        """
        Метод для читання вмісту текстового файлу.
        У випадку помилки генерує виняток FileCorrupted та логгує його у файл.
        """
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            raise FileCorrupted("Неможливо прочитати файл!")


    @logged(FileCorrupted, mode="console")
    def write(self, text: str):
        """
        Метод для повного перезапису вмісту файлу.
        У випадку помилки генерує виняток FileCorrupted та логгує його в консоль.
        """
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            raise FileCorrupted("Неможливо записати у файл!")


    @logged(FileCorrupted, mode="file")
    def append(self, text: str):
        """
        Метод для дописування тексту в кінець файлу.
        У випадку помилки генерує виняток FileCorrupted та логгує його у файл.
        """
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(text)
        except Exception:
            raise FileCorrupted("Неможливо дописати у файл!")

if __name__ == "__main__":
    """
    Точка входу в програму.
    Демонстрація роботи класу TextFileHandler.
    """

    file_path = "data_corrupted.txt"

    try:
        with open(file_path, "w") as f:
            f.write("test")

        handler = TextFileHandler(file_path)

        # 2. Штучне пошкодження шляху
        # Це змусить метод read/append згенерувати внутрішній OSError,
        # який буде перехоплений і перевиданий як FileCorrupted.
        handler.path = "/invalid/path/to/force/error.txt"

        print("Спроба читання, яка має викликати помилку та логування у файл...")
        
        # 3. Виклик декорованого методу read() з mode="file"
        handler.read() 
        
    except FileNotFound as e:
        print(f"[{type(e).__name__}] {e}")
        
    except FileCorrupted as e:
        # Виняток FileCorrupted буде перехоплений тут,
        # але ЛОГУВАННЯ У ФАЙЛ ВЖЕ ВІДБУЛОСЯ в декораторі.
        print(f"\n[{type(e).__name__}] {e}")

    # 4. Перевірка: тепер файл log.txt має існувати
    if os.path.exists("log.txt"):
        print("\n✅ Файл 'log.txt' успішно створено!")
        with open("log.txt", "r", encoding="utf-8") as f:
            print("--- Вміст log.txt ---")
            print(f.read())
            print("-----------------------")
    else:
        print("\n❌ Файл 'log.txt' не був створений.")