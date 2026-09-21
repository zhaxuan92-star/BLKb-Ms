from dataclasses import dataclass

from .parser import Program


@dataclass(frozen=True)
class VzBytecode:
    system_name: str
    instructions: list
    commands: dict


class VzCompiler:
    """Convert parsed Vz programs into simple executable tuples."""

    def compile(self, program: Program) -> VzBytecode:
        instructions = [
            (instruction.op, instruction.args, instruction.line)
            for instruction in program.instructions
        ]

        commands = {
            name: [
                (instruction.op, instruction.args, instruction.line)
                for instruction in command.instructions
            ]
            for name, command in program.commands.items()
        }

        return VzBytecode(program.system_name, instructions, commands)
