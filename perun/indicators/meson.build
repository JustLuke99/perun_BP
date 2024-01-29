perun_indicators_dir = perun_dir / 'indicators'

perun_indicators_files = files(
    '__init__.py',
    'indicator_manager.py',
)

py3.install_sources(
    perun_indicators_files,
    subdir: perun_indicators_dir,
)

subdir('abstract')
subdir('code_parsers')

