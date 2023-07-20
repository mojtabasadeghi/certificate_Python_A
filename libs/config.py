#!/usr/bin/env python3
#
# Copyright 2022 Emerja Corporation
#
import logging
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix='INTAKE',
    load_dotenv=True,
    settings_files=['settings.toml', '.secrets.toml'],
    environments=True
)

numeric_log_level = getattr(logging, settings.log_level.upper(), None)
if not isinstance(numeric_log_level, int):
    raise ValueError(f'Invalid log level: {settings.log_level}')
