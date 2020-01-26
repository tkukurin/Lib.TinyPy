# https://stackoverflow.com/questions/1057431/how-to-load-all-modules-in-a-folder


def __getall(glob):
  import importlib
  from os.path import dirname, basename, isfile
  from pathlib import Path
  modules = Path(dirname(__file__)).glob(glob)
  do_import = lambda f: isfile(f) and not f.name.endswith('__init__.py')
  return [basename(f)[:-len('.py')] for f in modules if do_import(f)]


__all__ = __getall('*.py')

