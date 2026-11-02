# SPDX-FileCopyrightText: 2025 OmniNode.ai Inc.
# SPDX-License-Identifier: MIT

"""Conformance suites for the lander protocols (OMN-22185).

Each ``suite_*.py`` module holds checks that take an adapter (or a harness around
one) and assert the protocol's behaviour. An adapter passes the suite by passing
every check; the in-memory adapter beside each protocol and any real adapter plug
into the same checks unchanged. Each suite has a positive control: a deliberately
broken adapter that the checks must refuse.
"""
