#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
信息采集模块

该模块提供基于API和SSH的信息采集功能：
- 基于API的信息采集（使用requests库）
- 基于SSH的信息采集（使用netmiko库）
"""

from .ssh_collector import SSHCollector
from .api_collector import APICollector

__all__ = ['SSHCollector', 'APICollector']