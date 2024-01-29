perun_indicators_code_parsers_dir = perun_indicators_dir / 'code_parsers'

perun_indicators_code_parsers_files = files(
    '__init__.py',
    'angr_parser.py',
    'ast_parser.py',
    'lizard_parser.py',
    'radon_parser.py',
)

py3.install_sources(
    perun_indicators_code_parsers_files,
    subdir: perun_indicators_code_parsers_dir,
)
