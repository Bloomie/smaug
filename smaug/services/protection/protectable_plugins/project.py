# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from oslo_log import log as logging

from smaug.common import constants
from smaug import resource
from smaug.services.protection import protectable_plugin

LOG = logging.getLogger(__name__)


class ProjectProtectablePlugin(protectable_plugin.ProtectablePlugin):
    _SUPPORT_RESOURCE_TYPE = constants.PROJECT_RESOURCE_TYPE

    def get_resource_type(self):
        return self._SUPPORT_RESOURCE_TYPE

    def get_parent_resource_types(self):
        return ()

    def list_resources(self):
        # TODO(yuvalbr) handle admin context for multiple projects?
        return resource.Resource(type=self._SUPPORT_RESOURCE_TYPE,
                                 id=self._context.project_id)

    def get_dependent_resources(self, parent_resource):
        pass
