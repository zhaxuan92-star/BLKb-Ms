import unittest

from vzcore.compiler import VzCompiler
from vzcore.parser import VzParser
from vzcore.runtime import VzRuntime, VzRuntimeError


class VzCoreTests(unittest.TestCase):
    def compile(self, source):
        program = VzParser().parse(source)
        return VzCompiler().compile(program)

    def test_parser_and_runtime(self):
        bytecode = self.compile(
            '''
            system "Test"
            set nation.name = "Vzcomm"
            set nation.population = 123
            command "hello" {
                print "Xin chào"
                show nation.name
                show nation.population
            }
            '''
        )

        output = []
        runtime = VzRuntime(
            bytecode,
            permissions={"admin.*"},
            output=output.append,
        )
        runtime.run_bootstrap()
        runtime.run_command("hello")

        self.assertEqual(runtime.get("nation.name"), "Vzcomm")
        self.assertEqual(runtime.get("nation.population"), 123)
        self.assertEqual(output, ["Xin chào", "Vzcomm", 123])

    def test_variable_reference(self):
        bytecode = self.compile(
            '''
            set name = "Vzcomm"
            command "hello" {
                print $name
            }
            '''
        )

        output = []
        runtime = VzRuntime(
            bytecode,
            output=output.append,
        )
        runtime.run_bootstrap()
        runtime.run_command("hello")
        self.assertEqual(output, ["Vzcomm"])

    def test_permission_denied(self):
        bytecode = self.compile(
            '''
            command "secret" {
                require secret.read
                print "hidden"
            }
            '''
        )

        runtime = VzRuntime(bytecode, output=lambda _: None)

        with self.assertRaises(VzRuntimeError):
            runtime.run_command("secret")

    def test_unclosed_command(self):
        with self.assertRaises(Exception):
            VzParser().parse('command "broken" {\n print "x"')

    def test_special_show_commands(self):
        bytecode = self.compile(
            '''
            set overview.text = "Overview"
            set leader.name = "Vz"
            command "display" {
                show overview
                show leader
            }
            '''
        )

        output = []
        runtime = VzRuntime(bytecode, output=output.append)
        runtime.run_bootstrap()
        runtime.run_command("display")
        self.assertEqual(output, ["Overview", "Vz"])


if __name__ == "__main__":
    unittest.main()
