from dataclasses import dataclass
from pathlib import Path
import re


class VzSyntaxError(Exception):
    """Raised when a Vz source file is invalid."""


@dataclass(frozen=True)
class Instruction:
    op: str
    args: tuple
    line: int


@dataclass
class CommandBlock:
    name: str
    instructions: list
    line: int


@dataclass
class Program:
    system_name: str
    instructions: list
    commands: dict


class VzParser:
    """Parse the small Vz language used by VzCore."""

    SET = re.compile(r"^set\s+([A-Za-z_][\w.]*)\s*=\s*(.+)$")
    PRINT = re.compile(r"^print\s+(.+)$")
    SHOW = re.compile(r"^show\s+(.+)$")
    COMMAND = re.compile(r'^command\s+"([^"]+)"\s*\{$')
    SYSTEM = re.compile(r'^system\s+"([^"]+)"$')
    REQUIRE = re.compile(r"^require\s+(.+)$")

    def parse_file(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file Vz: {path}")

        return self.parse(path.read_text(encoding="utf-8"), str(path))

    def parse(self, text, filename="<memory>"):
        system_name = "Unnamed Vz System"
        top = []
        commands = {}
        current = None

        for number, raw in enumerate(text.splitlines(), 1):
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            if line == "}":
                if current is None:
                    raise VzSyntaxError(
                        f"{filename}:{number}: '}}' không có block mở."
                    )
                if current.name in commands:
                    raise VzSyntaxError(
                        f"{filename}:{number}: command '{current.name}' bị trùng."
                    )
                commands[current.name] = current
                current = None
                continue

            match = self.SYSTEM.fullmatch(line)
            if match:
                if current is not None:
                    raise VzSyntaxError(
                        f"{filename}:{number}: system phải nằm ngoài command."
                    )
                system_name = match.group(1)
                continue

            match = self.COMMAND.fullmatch(line)
            if match:
                if current is not None:
                    raise VzSyntaxError(
                        f"{filename}:{number}: Không thể lồng command."
                    )
                current = CommandBlock(match.group(1), [], number)
                continue

            instruction = self.parse_instruction(line, number, filename)

            if current is None:
                top.append(instruction)
            else:
                current.instructions.append(instruction)

        if current is not None:
            raise VzSyntaxError(
                f"{filename}:{current.line}: "
                f"command '{current.name}' chưa đóng."
            )

        return Program(system_name, top, commands)

    def parse_instruction(self, line, number, filename):
        # Các lệnh đặc biệt phải được kiểm tra trước SHOW tổng quát.
        if line == "show overview":
            return Instruction("SHOW_OVERVIEW", (), number)

        if line == "show leader":
            return Instruction("SHOW_LEADER", (), number)

        match = self.SET.fullmatch(line)
        if match:
            return Instruction(
                "SET",
                (
                    match.group(1),
                    self.literal(match.group(2), number, filename),
                ),
                number,
            )

        match = self.PRINT.fullmatch(line)
        if match:
            return Instruction(
                "PRINT",
                (self.literal(match.group(1), number, filename),),
                number,
            )

        match = self.SHOW.fullmatch(line)
        if match:
            return Instruction("SHOW", (match.group(1).strip(),), number)

        match = self.REQUIRE.fullmatch(line)
        if match:
            permission = match.group(1).strip()
            if not permission:
                raise VzSyntaxError(
                    f"{filename}:{number}: Thiếu permission."
                )
            return Instruction("REQUIRE", (permission,), number)

        raise VzSyntaxError(
            f"{filename}:{number}: Cú pháp không hợp lệ: {line}"
        )

    def literal(self, value, number, filename):
        value = value.strip()

        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            return self.unescape(value[1:-1])

        if re.fullmatch(r"-?\d+", value):
            return int(value)

        if value.lower() == "true":
            return True

        if value.lower() == "false":
            return False

        if value.startswith("$"):
            if not re.fullmatch(r"\$[A-Za-z_][\w.]*", value):
                raise VzSyntaxError(
                    f"{filename}:{number}: Biến không hợp lệ: {value}"
                )
            return value

        raise VzSyntaxError(
            f"{filename}:{number}: Giá trị không hợp lệ: {value}"
        )

    @staticmethod
    def unescape(value):
        return (
            value.replace(r"\n", "\n")
            .replace(r"\t", "\t")
            .replace(r'\"', '"')
            .replace(r"\\", "\")
        )
