import inspect
import os

class TestImpl(object):
    def __init__(self):
        self.tests_output = None

    def __call__(self, func):
        """Test running wrapper

        Arguments:
            func Function -- wrapped function to evaluate
        """

        if os.environ.get("DISABLE_TESTING", False):
            return func

        self.tests_output = []
        tests_message = []

        test_func_name = f"{func.__name__}_test"
        test_func = None
        try:
            locals = inspect.currentframe().f_back.f_locals
            test_func = locals[test_func_name]
        except KeyError:
            tests_message = [f"Cannot locate test function named {test_func_name}"]

        if test_func:
            test_func(func)

        print("\n".join(
            [f"### TESTING {func.__name__}: PASSED {sum(1 if passed else 0 for passed, _ in self.tests_output)}/{len(self.tests_output)}"] +
            [f"# {o}" for o in tests_message] +
            [f"# {n}\t: {o[1]}" for n, o in enumerate(self.tests_output) if not o[0]] +
            ["###", ""]))

        self.tests_output = None
        return func

    def check_scope(self):
        if self.tests_output is None:
            raise Exception("Why are you calling test.equals outside a test function?")

    def equal(self, value, reference):
        self.check_scope()
        if value == reference:
            self.tests_output.append((True, "Passed"))
        else:
            self.tests_output.append((False, f"Failed: {value} is not equal to {reference}"))

    def true(self, prop):
        self.check_scope()
        if prop:
            self.tests_output.append((True, "Passed"))
        else:
            self.tests_output.append((False, f"Assertion failed"))

    def exception(self, lmbd, excpt=Exception):
        self.check_scope()
        try:
            lmbd()
        except Exception as e:
            if isinstance(e, excpt):
                self.tests_output.append((True, "Passed"))
            else:
                self.tests_output.append((False, f"Exception type {e}, not subclass of {excpt}"))
            return
        self.tests_output.append((False, f"No exception thrown."))

test = TestImpl()
