"""
Standard Date and Time formats for serialization/parsing.
All dates in the database are stored in UTC (ISO-8601).
"""

ISO_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
ISO_DATE_FORMAT = "%Y-%m-%d"

# UI Date Formats (only to be used for final display generation)
DISPLAY_DATETIME_FORMAT = "%d %b %Y, %H:%M"
DISPLAY_DATE_FORMAT = "%d %b %Y"
