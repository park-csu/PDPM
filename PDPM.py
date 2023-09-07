import os
import json
import argparse
import sys
import subprocess

class pdpm:
    def __init__(self):
        self.project_metadata = {}
        self.packages = {}
        self.virtualenv_name = ""
        self.python_interpreter = sys.executable
        self.cache_dir = os.path.join(os.getcwd(), ".cache", "packages")
        os.makedirs(self.cache_dir, exist_ok=True)

    def init(self, project_name, author, description, license):
        self.project_metadata = {
            "name": project_name,
            "author": author,
            "description": description,
            "license": license,
        }
        self.save_metadata()

    def set_python_interpreter(self, interpreter):
        self.python_interpreter = interpreter

    def create_virtualenv(self, env_name="venv"):
        self.virtualenv_name = env_name
        if os.name == "posix":
            subprocess.run([self.python_interpreter, "-m", "venv", self.virtualenv_name])
        elif os.name == "nt":
            subprocess.run([self.python_interpreter, "-m", "venv", self.virtualenv_name])
            self.activate_virtualenv()
        else:
            raise OSError("Unsupported operating system")

    def activate_virtualenv(self):
        activate_script = self.get_activate_script()
        try:
            if os.name == "posix":
                exec(open(activate_script).read(), dict(__file__=activate_script))
            elif os.name == "nt":
                exec([activate_script])
        except FileNotFoundError:
            print(f"Virtual environment '{self.virtualenv_name}' does not exist.")
            sys.exit(1)

    def get_activate_script(self):
        if os.name == "posix":
            return os.path.join(self.virtualenv_name, "bin", "activate_this.py")
        elif os.name == "nt":
            return os.path.join(self.virtualenv_name, "Scripts", "activate_this.py")
        else:
            raise OSError("Unsupported operating system")

    def deactivate_virtualenv(self):
        if os.name == "posix":
            deactivate_cmd = "deactivate"
            subprocess.run([deactivate_cmd], shell=True)
        elif os.name == "nt":
            deactivate_cmd = os.path.join(self.virtualenv_name, "Scripts", "deactivate.bat")
            subprocess.run([deactivate_cmd])
        else:
            raise OSError("Unsupported operating system")

    def add_package(self, package_name):
        self.packages[package_name] = "latest"
        self.save_metadata()

    def remove_package(self, package_name):
        if package_name in self.packages:
            del self.packages[package_name]
            self.save_metadata()

    def update_packages(self):
        for package_name, _ in self.packages.items():
            self.packages[package_name] = "latest"
        self.save_metadata()

    def lock_packages(self):
        with open("pdpm.lock", "w") as lock_file:
            json.dump(self.packages, lock_file, indent=2)

    def install_packages(self):
        if self.virtualenv_name:
            self.create_virtualenv()  # Re-create virtualenv if needed
            for package_name, package_version in self.packages.items():
                self.install_package(package_name, package_version)
        else:
            print("Please create a virtual environment first.")

    def install_package(self, package_name, package_version):
        package_spec = f"{package_name}=={package_version}"
        subprocess.run([self.python_interpreter, "-m", "pip", "install", package_spec])

    def list_packages(self):
        print("List of packages:")
        for package_name, package_version in self.packages.items():
            print(f"{package_name}=={package_version}")

    def save_metadata(self):
        with open("pyproject.toml", "w") as toml_file:
            toml_file.write("[project]\n")
            for key, value in self.project_metadata.items():
                toml_file.write(f"{key} = '{value}'\n")
            toml_file.write("\n[packages]\n")
            for package_name, package_version in self.packages.items():
                toml_file.write(f"{package_name} = '{package_version}'\n")

    def parse_args(self):
        parser = argparse.ArgumentParser(description="pdpm (Python Dependency Manager)")
        subparsers = parser.add_subparsers(title="commands", dest="command", required=True)

        init_parser = subparsers.add_parser("init", help="Initialize a new project")
        init_parser.add_argument("name", help="Project name")
        init_parser.add_argument("author", help="Project author")
        init_parser.add_argument("description", help="Project description")
        init_parser.add_argument("license", help="Project license")

        set_interpreter_parser = subparsers.add_parser(
            "set-python", help="Set the Python interpreter for the virtualenv"
        )
        set_interpreter_parser.add_argument(
            "interpreter", help="Python interpreter (e.g., python3.8)"
        )

        create_env_parser = subparsers.add_parser(
            "create-env", help="Create a virtual environment"
        )
        create_env_parser.add_argument(
            "env_name", help="Name of the virtual environment"
        )

        add_package_parser = subparsers.add_parser(
            "add", help="Add a package to the project"
        )
        add_package_parser.add_argument(
            "package_name", help="Name of the package to add"
        )

        remove_package_parser = subparsers.add_parser(
            "remove", help="Remove a package from the project"
        )
        remove_package_parser.add_argument(
            "package_name", help="Name of the package to remove"
        )

        subparsers.add_parser("update", help="Update all packages in the project")
        subparsers.add_parser("lock", help="Lock the project's packages in pdpm.lock")
        subparsers.add_parser("install", help="Install packages specified in pdpm.lock")
        subparsers.add_parser("list", help="List packages in the project")

        args = parser.parse_args()

        if args.command == "init":
            self.init(args.name, args.author, args.description, args.license)
        elif args.command == "set-python":
            self.set_python_interpreter(args.interpreter)
        elif args.command == "create-env":
            self.create_virtualenv(args.env_name)
        elif args.command == "add":
            self.add_package(args.package_name)
        elif args.command == "remove":
            self.remove_package(args.package_name)
        elif args.command == "update":
            self.update_packages()
        elif args.command == "lock":
            self.lock_packages()
        elif args.command == "install":
            self.install_packages()
        elif args.command == "list":
            self.list_packages()

if __name__ == "__main__":
    pdpm = pdpm()
    pdpm.parse_args()
