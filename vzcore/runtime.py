class VzRuntimeError(Exception):
    """Raised when a Vz program fails during execution."""


class VzRuntime:
    def __init__(self, bytecode, data=None, permissions=None, output=None):
        self.bytecode = bytecode
        self.vars = dict(data or {})
        self.permissions = set(permissions or ())
        self.running = True
        self.output = output or print

    def resolve(self, value):
        if isinstance(value, str) and value.startswith("$"):
            return self.vars.get(value[1:], "")
        return value

    def get(self, key):
        return self.vars.get(key, "")

    def set(self, key, value):
        self.vars[key] = self.resolve(value)

    def require(self, permission):
        if permission in self.permissions or "admin.*" in self.permissions:
            return
        raise VzRuntimeError(f"Permission denied: {permission}")

    def execute(self, instructions):
        for op, args, line in instructions:
            try:
                if op == "SET":
                    self.set(args[0], args[1])

                elif op == "PRINT":
                    self.output(self.resolve(args[0]))

                elif op == "SHOW":
                    key = args[0]
                    if key.startswith("$"):
                        self.output(self.resolve(key))
                    else:
                        self.output(self.get(key))

                elif op == "SHOW_OVERVIEW":
                    self.output(self.get("overview.text"))

                elif op == "SHOW_LEADER":
                    self.output(self.get("leader.name"))

                elif op == "REQUIRE":
                    self.require(args[0])

                else:
                    raise VzRuntimeError(f"Opcode không tồn tại: {op}")

            except VzRuntimeError:
                raise
            except Exception as error:
                raise VzRuntimeError(f"line {line}: {error}") from error

    def run_bootstrap(self):
        self.execute(self.bytecode.instructions)

    def run_command(self, name):
        if name not in self.bytecode.commands:
            raise VzRuntimeError(f"Command không tồn tại: {name}")
        self.execute(self.bytecode.commands[name])
