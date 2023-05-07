import os
import shutil


class File:
    def __init__(self, path):
        """
        Initialize a File object.

        Args:
            path (str): The path to the file.
        """
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)

    def read_bytes(self):
        """
        Read and return the contents of the file as bytes.

        Returns:
            bytes: The contents of the file.
        """
        with open(self.path, 'rb') as f:
            return f.read()

    def change_path(self, new_path):
        """
        Change the path of the file.

        Args:
            new_path (str): The new path for the file.
        """
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        os.rename(self.path, new_path)
        self.path = new_path
        self.name = os.path.basename(new_path)


class Directory:
    def __init__(self, path):
        """
        Initialize a Directory object.

        Args:
            path (str): The path to the directory.
        """
        self.path = path
        self.name = os.path.basename(path)
        self.subdirectories = []
        self.files = []

        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                subdirectory = Directory(full_path)
                self.subdirectories.append(subdirectory)
            else:
                file = File(full_path)
                self.files.append(file)

    def create(self, parent_path=None):
        """
        Recursively create the directory and its contents.

        Args:
            parent_path (str, optional): The parent path for the directory. Defaults to None.
        """
        if parent_path is None:
            parent_path = self.path

        directory_path = os.path.join(parent_path, self.name)
        os.makedirs(directory_path, exist_ok=True)

        for file in self.files:
            file_path = os.path.join(directory_path, file.name)
            with open(file_path, 'wb') as f:
                f.write(file.read_bytes())

        for subdirectory in self.subdirectories:
            subdirectory.create(directory_path)

    def change_file_path(self, file_path, new_path):
        """
        Change the path of a file within the directory.

        Args:
            file_path (str): The current path of the file.
            new_path (str): The new path for the file.
        """
        for file in self.files:
            if file.path == file_path:
                file.change_path(new_path)
                break

        # Update subdirectories recursively
        for subdirectory in self.subdirectories:
            subdirectory.change_file_path(file_path, new_path)

    def change_folder_path(self, folder_path, new_path):
        """
        Change the path of a subdirectory within the directory.

        Args:
            folder_path (str): The current path of the subdirectory.
            new_path (str): The new path for the subdirectory.
        """
        for subdirectory in self.subdirectories:
            if subdirectory.path == folder_path:
                subdirectory.change_path(new_path)
                break

        # Update subdirectories recursively
        for subdirectory in self.subdirectories:
            subdirectory.change_folder_path(folder_path, new_path)

    def change_path(self, new_path):
        """
        Change the path of the directory.

        Args:
            new_path (str): The new path for the directory.
        """
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(self.path, os.path.dirname(new_path))
        os.chdir(os.path.dirname(new_path))
        os.rename(self.name, os.path.basename(new_path))
        self.path = new_path
        self.name = os.path.basename(new_path)


# Create a Directory object
new_directory = Directory(r'C:\Users\orico\OneDrive\שולחן העבודה\FS')

# Call the create() method to create the directory with its files and subdirectories
new_directory.create(r'C:\Users\orico\PycharmProjects\OOP')

# new_directory.change_file_path(r"C:\Users\orico\OneDrive\שולחן העבודה\FS\try4\test_thread.py",
#    r"C:\Users\orico\OneDrive\שולחן העבודה\FS\test_thread1.py")
# TO DO use change_file_path for rename/move file. If the file was moved outside the shared folder, use delete.

new_directory.change_folder_path(r"C:\Users\orico\OneDrive\שולחן העבודה\FS\try4", r"C:\Users\orico\OneDrive\שולחן "
                                                                                  r"העבודה\FS\test\try")