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

"""
Manage all operations.
"""

from smaug import exception
from smaug.i18n import _
from smaug.operationengine import operations


class OperationManager(object):
    """Manage all operation classes which are defined at operations dir."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not OperationManager._instance:
            OperationManager._instance = super(
                OperationManager, cls).__new__(
                    cls, *args, **kwargs)
        return OperationManager._instance

    def __init__(self):
        super(OperationManager, self).__init__()

        all_cls = operations.all_operations()
        self._operation_cls_map = {cls.OPERATION_TYPE: cls
                                   for cls in all_cls}

    def _get_operation_cls(self, operation_type):
        if operation_type not in self._operation_cls_map:
            msg = (_("Invalid operation type:%s") % operation_type)
            raise exception.InvalidInput(msg)

        return self._operation_cls_map[operation_type]

    def check_operation_definition(self, operation_type, operation_definition):
        """Check operation definition.

        :param operation_type: the type of operation
        :param operation_definition: the definition of operation
        :raise InvalidInput if the operation_type is invalid or
               InvalidOperationDefinition if operation_definition is invalid
        """
        cls = self._get_operation_cls(operation_type)
        cls.check_operation_definition(operation_definition)

    def execute_operation(self, operation_type, project_id,
                          operation_definition):
        """Execute operation.

        :param operation_type: the type of operation
        :param project_id: the id of tenant
        :param operation_definition: the definition of operation
        :raise InvalidInput if the operation_type is invalid.
        """
        cls = self._get_operation_cls(operation_type)
        cls.execute(project_id, operation_definition)
