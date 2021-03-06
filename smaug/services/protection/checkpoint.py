#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from uuid import uuid4 as uuid

from oslo_config import cfg
from oslo_log import log as logging

from smaug.services.protection.bank_plugin import BankSection

CONF = cfg.CONF

LOG = logging.getLogger(__name__)

_INDEX_FILE_SUFFIX = ".index.json"


def _checkpoint_id_to_index_file(checkpoint_id):
    return "/%s%s" % (checkpoint_id, _INDEX_FILE_SUFFIX)


class Checkpoint(object):
    VERSION = "0.9"
    SUPPORTED_VERSIONS = ["0.9"]

    def __init__(self, bank_section, checkpoint_id):
        self._id = checkpoint_id
        self._index_file_path = _checkpoint_id_to_index_file(checkpoint_id)
        self._bank_section = bank_section
        self.reload_meta_data()

    @property
    def bank_section(self):
        return self._bank_section

    @property
    def id(self):
        return self._id

    @property
    def status(self):
        # TODO(saggi): check for valid values and transitions
        return self._md_cache["status"]

    @status.setter
    def status(self, value):
        self._md_cache["status"] = value

    def _is_supported_version(self, version):
        return version in self.SUPPORTED_VERSIONS

    def _assert_supported_version(self, new_md):
        if new_md["version"] not in self.SUPPORTED_VERSIONS:
            # Something bad happend invalidate the object
            self._md_cache = None
            self._bank_section = None
            raise RuntimeError(
                "Checkpoint was created in an unsupported version")

    def reload_meta_data(self):
        new_md = self._bank_section.get_object(self._index_file_path)
        self._assert_supported_version(new_md)
        self._md_cache = new_md

    @classmethod
    def _generate_id(self):
        return str(uuid())

    @classmethod
    def get_by_section(cls, bank_section, checkpoint_id):
        return Checkpoint(bank_section, checkpoint_id)

    @classmethod
    def create_in_section(cls, bank_section, checkpoint_id=None):
        checkpoint_id = checkpoint_id or cls._generate_id()
        bank_section.create_object(
            key=_checkpoint_id_to_index_file(checkpoint_id),
            value={
                "version": cls.VERSION,
                "id": checkpoint_id,
                "status": "protecting",
            }
        )
        return Checkpoint(bank_section, checkpoint_id)

    def commit(self):
        self._bank_section.create_object(
            key=self._index_file_path,
            value=self._md_cache,
        )

    def purge(self):
        """Purge the index file of the checkpoint.

        Can only be done if the checkpoint has no other files apart from the
        index.
        """
        all_objects = self._bank_section.list_objects(prefix=self.id)
        if (
            len(all_objects) == 1
            and all_objects[0] == self._index_file_path
        ) or len(all_objects) == 0:
            self._bank_section.delete_object(self._index_file_path)
        else:
            raise RuntimeError("Could not delete: Checkpoint is not empty")


class CheckpointCollection(object):

    def __init__(self, bank):
        super(CheckpointCollection, self).__init__()
        self._bank = bank
        self._checkpoints_section = BankSection(bank, "/checkpoints")

    def list_ids(self, limit=None, marker=None):
        if marker is not None:
            marker = _checkpoint_id_to_index_file(marker)

        return [key[:-len(_INDEX_FILE_SUFFIX)]
                for key in self._checkpoints_section.list_objects(
                    limit=limit,
                    marker=marker)
                ]

    def get(self, checkpoint_id):
        # TODO(saggi): handle multiple instances of the same checkpoint
        return Checkpoint.get_by_section(self._checkpoints_section,
                                         checkpoint_id)

    def create(self, plan):
        # TODO(saggi): Serialize plan to checkpoint. Will be done in
        # future patches.
        return Checkpoint.create_in_section(self._checkpoints_section)
