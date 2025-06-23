import datetime

from marshmallow import fields

TYPE_MAPPING = {
    str: fields.String,
    int: fields.Integer,
    bool: fields.Boolean,
    float: fields.Float,
    datetime.date: fields.Date,
    datetime.datetime: fields.DateTime,
}
