# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at:
#
#    http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the
# License.

# Python 2/3 compatibility
from decimal import Decimal

import pytest

from amazon.ion.core import Timestamp, TimestampPrecision, record
from tests import parametrize, listify


class _P(record('timestamps', 'expected_value')):
    def __str__(self):
        return self.desc


MISSING_MICROSECOND = [
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, None,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=0
        ), 0),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, None,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=Decimal('0.123456')
        ), 123456),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, None,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=Decimal('0.123456789')
        ), 123456),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, None,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=Decimal('0.000123')
        ), 123),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, None,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=Decimal('0.123000')
        ), 123000)
]


MISSING_FRACTIONAL_PRECISION = [
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 0,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=None
        ), 0),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 123456,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=None
        ), Decimal('0.123456')),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 123,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=None
        ), Decimal('0.000123')),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 123000,
        precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=None
        ), Decimal('0.123000'))
]


LARGE_MICROSECOND_FIELD = [
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 12345678,
        precision=TimestampPrecision.SECOND, fractional_precision=8, fractional_seconds=Decimal('0.12345678')
        ), 123456),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 9999999,
        precision=TimestampPrecision.SECOND, fractional_precision=7, fractional_seconds=Decimal('0.9999999')
        ), 999999),
    (Timestamp(
        2011, 1, 1,
        0, 0, 0, 1337894870,
        precision=TimestampPrecision.SECOND, fractional_precision=10, fractional_seconds=Decimal('0.1337894870')
        ), 133789),
]


@listify
def event_type_parameters(list_name):
    print(list_name)
    for timestamp, expected_val in list_name:
        yield _P(
            timestamps=timestamp,
            expected_value=expected_val,
        )


@parametrize(*event_type_parameters(MISSING_MICROSECOND))
def test_missing_microsecond(item):
    timestamp = item.timestamps
    expected_microsecond = item.expected_value
    assert timestamp.microsecond == expected_microsecond


@parametrize(*event_type_parameters(MISSING_FRACTIONAL_PRECISION))
def test_missing_fractional_seconds(item):
    timestamp = item.timestamps
    expected_fractional_second = item.expected_value
    assert timestamp.fractional_seconds == expected_fractional_second


@parametrize(*event_type_parameters(LARGE_MICROSECOND_FIELD))
def test_large_microsecond_field_value(item):
    timestamp = item.timestamps
    expected_microsecond = item.expected_value
    assert timestamp.microsecond == expected_microsecond


def test_invalid_timestamp_constructor_parameters():
    with pytest.raises(ValueError):
        # Non-equivalent microseconds and fractional seconds.
        Timestamp(
            2011, 1, 1,
            0, 0, 0, 123456,
            precision=TimestampPrecision.SECOND, fractional_precision=6, fractional_seconds=0
        )

    with pytest.raises(ValueError):
        # Fractional seconds with no fractional precision.
        Timestamp(
            2011, 1, 1,
            0, 0, 0, None,
            precision=TimestampPrecision.SECOND, fractional_precision=None, fractional_seconds=Decimal('0.123')
        )

    with pytest.raises(ValueError):
        # Fractional precision is less than 1.
        Timestamp(
            2011, 1, 1,
            0, 0, 0, 0,
            precision=TimestampPrecision.SECOND, fractional_precision=0, fractional_seconds=0
        )

    with pytest.raises(ValueError):
        # Fractional seconds is greater than 1.
        Timestamp(
            2011, 1, 1,
            0, 0, 0, 0,
            precision=TimestampPrecision.SECOND, fractional_precision=1, fractional_seconds=2
        )

