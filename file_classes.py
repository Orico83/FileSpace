import os
import shutil

FOLDER = r'.\ServerFolder'


class File:
    def __init__(self, path):
        """
        Initialize a File object.
        :param path:: The path to the file.
        """
        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.rel_path = None
        with open(self.path, "rb") as f:
            data = f.read()
        self.data = data

    def create(self, parent_path=None):
        """
        Creates the file in the parent path.
        :param parent_path: path to the file. Defaults to None.
        """
        if "ServerFolder" in self.path:
            self.rel_path = os.path.relpath(self.path, "./ServerFolder")
            self.path = os.path.join(FOLDER, self.rel_path)
        elif r"Desktop\FS" in self.path:
            self.rel_path = self.path.split("Desktop/FS")[-1]
            self.path = os.path.join(FOLDER, self.rel_path)

        if parent_path is None:
            parent_path = self.path
        if os.path.exists(parent_path):
            file = File(parent_path)
            if file.data != self.data:
                with open(parent_path, 'wb'):
                    pass
                with open(parent_path, 'wb') as f:
                    f.write(self.data)
        else:
            with open(parent_path, 'wb') as f:
                f.write(self.data)


class Directory:
    def __init__(self, path):
        """
        Initialize a Directory object.
        :param path: The path to the directory.
        """
        self.path = path
        self.name = os.path.basename(path)
        self.subdirectories = []
        self.files = []
        self.size = 0  # Initialize the size attribute to zero

        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                subdirectory = Directory(full_path)
                self.subdirectories.append(subdirectory)
                self.size += subdirectory.size  # Add subdirectory size to the current directory's size
            else:
                file = File(full_path)
                self.files.append(file)
                self.size += file.size  # Add file size to the current directory's size

    def create(self, parent_path=None):
        """
        Recursively create the directory and its contents.
        :param parent_path:The parent path for the directory. Defaults to None.
        """
        if parent_path is None:
            parent_path = self.path

        os.makedirs(parent_path, exist_ok=True)

        # Remove non-matching files and subdirectories
        existing_files = [file.name for file in self.files]
        existing_subdirectories = [subdir.name for subdir in self.subdirectories]

        for item_name in os.listdir(parent_path):
            item_path = os.path.join(parent_path, item_name)

            if os.path.isfile(item_path) and item_name not in existing_files:
                os.remove(item_path)

            if os.path.isdir(item_path) and item_name not in existing_subdirectories:
                shutil.rmtree(item_path)

        for file in self.files:
            file.create(os.path.join(parent_path, file.name))

        for subdirectory in self.subdirectories:
            subdirectory.create(os.path.join(parent_path, subdirectory.name))
        return Directory(parent_path)

    def change_path(self, new_path):
        """
        Change the path of the directory.
        :param new_path: The new path for the directory.
        :returns: None
        """
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(self.path, os.path.dirname(new_path))
        os.chdir(os.path.dirname(new_path))
        os.rename(self.name, os.path.basename(new_path))
        self.path = new_path
        self.name = os.path.basename(new_path)

    def search_files(self, keyword):    # Not used yet
        """
        Search for files containing the specified keyword in their names within the directory and its subdirectories.

        :param keyword: The keyword to search for in file names.
        :return: A list of matching File objects.
        """
        matching_files = []
        for file in self.files:
            if keyword.upper() in file.name.upper():
                matching_files.append(file)

        for subdirectory in self.subdirectories:
            matching_files.extend(subdirectory.search_files(keyword))

        return matching_files
