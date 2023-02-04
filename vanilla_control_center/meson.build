pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'vanilla_control_center')
gnome = import('gnome')

gnome.compile_resources('vanilla-control-center',
  'vanilla-control-center.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'vanilla-control-center.in',
  output: 'vanilla-control-center',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('backends')

vanilla_control_center_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'driver.py',
  'program.py',
  'run_async.py',
  'container.py',
  'dialog_installation.py',
]

install_data(vanilla_control_center_sources, install_dir: moduledir)
