
from unittest import TestCase
import datadiligence as dd
import datadiligence.exceptions
from samples.custom import CustomEvaluator, CustomRule


class BootstrapTests(TestCase):

    def test_exceptions(self):
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.is_allowed, "x")
        self.assertRaises(dd.exceptions.NotEvaluator, dd.register_evaluator, None, "y")

        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom0")
        self.assertRaises(dd.exceptions.EvaluatorAlreadyRegistered,
                          dd.register_evaluator, custom_evaluator, "custom0")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.deregister_evaluator, "not-used")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.get_evaluator, "not-used")
        self.assertRaises(dd.exceptions.DefaultEvaluatorNotFound, dd.is_allowed, example="not-used")

    def test_load_defaults(self):
        # reset evaluators
        for key in dd.list_evaluators():
            dd.deregister_evaluator(key)

        dd.load_defaults()
        self.assertTrue(isinstance(dd.get_evaluator("preprocess"), dd.PreprocessEvaluator))
        self.assertTrue(isinstance(dd.get_evaluator("postprocess"), dd.PostprocessEvaluator))
        self.assertEqual(len(dd.list_evaluators()), 3)

    def test_register_evaluator(self):
        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom1")
        self.assertEqual(dd.get_evaluator("custom1"), custom_evaluator)

    def test_deregister_evaluator(self):
        custom_evaluator = dd.Evaluator()
        dd.register_evaluator(custom_evaluator, "custom3")
        self.assertEqual(dd.get_evaluator("custom3"), custom_evaluator)
        dd.deregister_evaluator("custom3")
        self.assertRaises(dd.exceptions.EvaluatorNotRegistered, dd.deregister_evaluator, "custom3")

    def test_is_allowed(self):
        custom_evaluator = CustomEvaluator()
        custom_evaluator.add_rule(CustomRule())
        dd.register_evaluator(custom_evaluator, "custom2")
        self.assertFalse(dd.is_allowed("custom2", sample="www.google.com"))
        self.assertTrue(dd.is_allowed("custom2", sample="www.example.com"))
