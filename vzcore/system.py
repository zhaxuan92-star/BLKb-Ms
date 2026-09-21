from pathlib import Path

from .compiler import VzBytecode, VzCompiler
from .parser import VzParser
from .runtime import VzRuntime, VzRuntimeError


class VzSystem:
    """High-level loader and interactive shell for VzCore."""

    def __init__(self, root=None):
        self.root = Path(root or Path(__file__).resolve().parent.parent)
        self.code_dir = self.root / "examples"
        self.data_dir = self.root / "data"
        self.parser = VzParser()
        self.compiler = VzCompiler()
        self.runtime = None

    def load(self):
        programs = [
            self.parser.parse_file(path)
            for path in sorted(self.code_dir.glob("*.vz"))
        ]

        if not programs:
            raise RuntimeError("Không tìm thấy file .vz.")

        system_name = programs[0].system_name
        instructions = []
        commands = {}

        for program in programs:
            bytecode = self.compiler.compile(program)
            instructions.extend(bytecode.instructions)
            commands.update(bytecode.commands)

        final_bytecode = VzBytecode(system_name, instructions, commands)

        self.runtime = VzRuntime(
            final_bytecode,
            permissions=self.load_permissions(),
        )

        self.load_data()
        self.runtime.run_bootstrap()

    def load_permissions(self):
        file = self.root / "System"
        if not file.exists():
            return set()

        permissions = set()
        for raw in file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#"):
                permissions.add(line)
        return permissions

    def load_data(self):
        file = self.data_dir / "config.vzdata"
        if not file.exists():
            return

        for number, raw in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise RuntimeError(
                    f"{file}:{number}: thiếu '=' trong dữ liệu."
                )

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            elif value.lstrip("-").isdigit():
                value = int(value)
            elif value.lower() in {"true", "false"}:
                value = value.lower() == "true"
            else:
                raise RuntimeError(
                    f"{file}:{number}: giá trị dữ liệu không hợp lệ."
                )

            self.runtime.set(key, value)

    def execute(self, command):
        command = command.strip()
        if not command:
            return

        if command in {"exit", "quit"}:
            self.runtime.running = False
            return

        if command == "help":
            print(
                """
VzCore commands:
  help
  info
  leader
  overview
  show <key>
  set <key> = <value>
  run <command>
  permissions
  reload
  exit
"""
            )
            return

        if command == "info":
            print(f"System: {self.runtime.bytecode.system_name}")
            print(f"Variables: {len(self.runtime.vars)}")
            print(
                "Commands: "
                + ", ".join(sorted(self.runtime.bytecode.commands))
            )
            return

        if command == "permissions":
            for permission in sorted(self.runtime.permissions):
                print(permission)
            return

        if command == "leader":
            command = "run leader"

        elif command == "overview":
            command = "run overview"

        if command == "reload":
            self.load()
            print("[VzCore] Reloaded.")
            return

        if command.startswith("run "):
            self.runtime.run_command(command[4:].strip())
            return

        if command.startswith("show "):
            print(self.runtime.get(command[5:].strip()))
            return

        if command.startswith("set ") and "=" in command:
            left, right = command[4:].split("=", 1)
            key = left.strip()
            value = self.parse_shell_value(right.strip())
            self.runtime.set(key, value)
            print(f"{key} = {value}")
            return

        print(f"Lệnh không tồn tại: {command}")

    @staticmethod
    def parse_shell_value(value):
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        if value.lstrip("-").isdigit():
            return int(value)
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        raise VzRuntimeError(
            "Giá trị phải là string, integer hoặc boolean."
        )

    def start(self):
        print("======= VINH QUANG VZ =======")
        print("VzCore 3.0")
        print("Python = bootstrap/runtime")
        print(".vz = system logic")

        try:
            self.load()
        except Exception as error:
            print(f"[VZ-ERROR] {error}")
            return

        while self.runtime.running:
            try:
                command = input("Vz> ")
                self.execute(command)
            except (KeyboardInterrupt, EOFError):
                print("\nĐã thoát.")
                break
            except Exception as error:
                print(f"[VZ-ERROR] {error}")
