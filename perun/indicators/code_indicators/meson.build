perun_indicators_code_parsers_dir = perun_indicators_dir / 'code_indicators'

perun_indicators_code_parsers_files = files(
    '__init__.py',
    'angr_indicator.py',
    'ast_indicator.py',
    'lizard_indicator.py',
    'radon_indicator.py',
)

py3.install_sources(
    perun_indicators_code_parsers_files,
    subdir: perun_indicators_code_parsers_dir,
)
