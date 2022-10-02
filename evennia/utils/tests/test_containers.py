import unittest

from evennia.utils import containers
from django.conf import settings
from evennia.utils.utils import class_from_module

_BASE_SCRIPT_TYPECLASS = class_from_module(settings.BASE_SCRIPT_TYPECLASS)

class GoodScript(_BASE_SCRIPT_TYPECLASS):
  pass

class BadScript:
  """Not subclass of _BASE_SCRIPT_TYPECLASS,"""
  pass

class WorseScript(_BASE_SCRIPT_TYPECLASS):
  """objects will fail upon call"""
  @property
  def objects(self):
    from evennia import module_that_doesnt_exist

class TestGlobalScriptContainer(unittest.TestCase):

  def setUp(self):
    settings.GLOBAL_SCRIPTS = {}

  def patch_global_scripts(self, adict):
    settings.GLOBAL_SCRIPTS.update(adict)

  def test_init_with_no_scripts(self):
    gsc = containers.GlobalScriptContainer()

    self.assertEqual(len(gsc.loaded_data), 0)

  def test_init_with_typeclassless_script(self):
    self.patch_global_scripts({'script_name': {}})

    gsc = containers.GlobalScriptContainer()

    self.assertEqual(len(gsc.loaded_data), 1)
    self.assertIn('script_name', gsc.loaded_data)

  def test_start_with_no_scripts(self):
    gsc = containers.GlobalScriptContainer()

    gsc.start()

    self.assertEqual(len(gsc.typeclass_storage), 0)

  def test_start_with_typeclassless_script_defaults_to_base(self):
    self.patch_global_scripts({'script_name': {}})
    gsc = containers.GlobalScriptContainer()

    gsc.start()

    self.assertEqual(len(gsc.typeclass_storage), 1)
    self.assertIn('script_name', gsc.typeclass_storage)
    self.assertEqual(gsc.typeclass_storage['script_name'], _BASE_SCRIPT_TYPECLASS)

  def test_start_with_typeclassed_script_loads_it(self):
    self.patch_global_scripts({'script_name': {'typeclass': 'evennia.utils.tests.test_containers.GoodScript'}})
    gsc = containers.GlobalScriptContainer()

    gsc.start()

    self.assertEqual(len(gsc.typeclass_storage), 1)
    self.assertIn('script_name', gsc.typeclass_storage)
    self.assertEqual(gsc.typeclass_storage['script_name'], GoodScript)

  def test_start_with_bad_typeclassed_script_skips_it(self):
    self.patch_global_scripts({'script_name': {'typeclass': 'evennia.utils.tests.test_containers.BadScript'}})
    gsc = containers.GlobalScriptContainer()

    gsc.start()

    self.assertEqual(len(gsc.typeclass_storage), 0)
    self.assertNotIn('script_name', gsc.typeclass_storage)

  def test_start_with_worst_typeclassed_script_skips_it(self):
    self.patch_global_scripts({'script_name': {'typeclass': 'evennia.utils.tests.test_containers.WorstScript'}})
    gsc = containers.GlobalScriptContainer()

    gsc.start()

    self.assertEqual(len(gsc.typeclass_storage), 0)
    self.assertNotIn('script_name', gsc.typeclass_storage)
