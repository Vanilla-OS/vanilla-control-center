pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
backendsdir = join_paths(pkgdatadir, 'vanilla_control_center/backends')

sources = [
  '__init__.py',
  'apx.py',
  'vso.py',
  'exceptions.py',
]

install_data(sources, install_dir: backendsdir)