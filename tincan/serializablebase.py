"""
    Copyright 2014 Rustici Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

import json
from base import Base
from version import Version

"""
.. module:: serializablebase
   :synopsis: A base object that provides the common initializer from :mod:`base`
   as well as common serialization functionality

"""


class SerializableBase(Base):

    @classmethod
    def from_json(cls, json_data):
        """Tries to convert a JSON representation to an object of the same
        type as self

        A class can provide a _fromJSON implementation in order to do specific
         type checking or other custom implementation details. This method
        will throw a ValueError for invalid JSON, a TypeError for
        improperly constructed, but valid JSON, and any custom errors
        that can be be propagated from class constructors.

        :param json_data: The JSON string to convert
        :type json_data: str

        """
        data = json.loads(json_data)
        result = cls(**data)
        if "_from_json" in dir(result):
            result._from_json()
        return result

    def to_json(self, version=Version.latest):
        """Tries to convert an object into a JSON respresentation and return
        the resulting string

        An Object can define how it is serialized by providing an _as_version()
        implementation. A caller may further define how the object is serialized
        by passing in a custom encoder. The default encoder will ignore
        properties of an object that are None at the time of serialization.

        :param version: The version to which the object must be serialized to.
        This will default to the latest version supported by the library.
        :type version: str
        :param encoder: The custom encoder. The default is described above.
        :type encoder: json.JSONEncoder

        """
        return json.dumps(self.as_version(version))

    def as_version(self, version=Version.latest):
        """Returns a dict that has been modified based on versioning
        in order to be represented in JSON properly

        A class can provide an _as_version(self, version)
        implementation in order to tailor a more specific representation

        :param version: the relevant version. This allows for variance
         between versions
        :type version: str

        """
        result = {}
        it = dict(self) if isinstance(self, dict) else dict(vars(self))
        for k, v in it.iteritems():
            if hasattr(v, "_as_version"):
                result[k] = v._as_version(version)
            elif isinstance(v, SerializableBase):
                result[k] = v.as_version(version)
            else:
                result[k] = v
        result = self._filter_none(result)
        return result

    def _filter_none(self, obj):
        """Filters out attributes set to None prior to serialization, and
        returns a new object without those attributes. This saves
        the serializer from sending empty bytes over the network. This method also
        fixes the keys to look as expected by ignoring a leading '_' if it
        is present.

        :param obj: the dictionary representation of an object that may have
        None attributes
        :type obj: dict

        """
        result = {}
        for k, v in obj.iteritems():
            if v is not None:
                if k.startswith('_'):
                    k = k[1:]
                result[k] = v
        return result