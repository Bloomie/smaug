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

import mock

from smaug.resource import Resource
from smaug.services.protection import manager
from smaug.services.protection import protectable_registry
from smaug.tests import base
from smaug.tests.unit.protection import fakes


class ProtectionServiceTest(base.TestCase):
    def setUp(self):
        super(ProtectionServiceTest, self).setUp()
        self.pro_manager = manager.ProtectionManager()
        self.protection_plan = fakes.fake_protection_plan()

    @mock.patch.object(protectable_registry.ProtectableRegistry,
                       'list_resource_types')
    def test_list_protectable_types(self, mocker):
        excepted = ["OS::Nova::Server",
                    "OS::Cinder::Volume"]
        mocker.return_value = excepted
        result = self.pro_manager.list_protectable_types(None)
        self.assertEqual(excepted, result)

    def test_show_protectable_type(self):
        def mock_plugins(self):
            self._plugin_map = {
                "OS::Nova::Server": server_plugin,
                "OS::Cinder::Volume": volume_plugin
            }

        server_plugin = fakes.FakeProtectablePlugin()
        server_plugin.get_resource_type = mock.MagicMock(
            return_value="OS::Nova::Server")
        volume_plugin = fakes.FakeProtectablePlugin()
        volume_plugin.get_parent_resource_types = mock.MagicMock(
            return_value=["OS::Nova::Server"])

        protectable_registry.ProtectableRegistry.load_plugins = mock_plugins

        result = self.pro_manager.show_protectable_type(None,
                                                        "OS::Nova::Server")
        self.assertEqual({
            "name": "OS::Nova::Server",
            "dependent_types": ["OS::Cinder::Volume"]},
            result)

    @mock.patch.object(protectable_registry.ProtectableRegistry,
                       'show_resource')
    def test_show_protectable_instance(self, mocker):
        mocker.return_value = Resource(type='OS::Nova::Server',
                                       id='123456',
                                       name='name123')
        fake_cntx = mock.MagicMock()

        result = self.pro_manager.show_protectable_instance(
            fake_cntx, 'OS::Nova::Server', '123456')
        self.assertEqual({'id': '123456', 'name': 'name123'},
                         result)

    @mock.patch.object(protectable_registry.ProtectableRegistry,
                       'list_resources')
    def test_list_protectable_instances(self, mocker):
        mocker.return_value = [Resource(type='OS::Nova::Server',
                                        id='123456',
                                        name='name123'),
                               Resource(type='OS::Nova::Server',
                                        id='654321',
                                        name='name654')]
        fake_cntx = mock.MagicMock()

        result = self.pro_manager.list_protectable_instances(
            fake_cntx, 'OS::Nova::Server')
        self.assertEqual([{'id': '123456', 'name': 'name123'},
                          {'id': '654321', 'name': 'name654'}],
                         result)

    @mock.patch.object(protectable_registry.ProtectableRegistry,
                       'fetch_dependent_resources')
    def test_list_protectable_dependents(self, mocker):
        mocker.return_value = [Resource(type='OS::Cinder::Volume',
                                        id='123456', name='name123'),
                               Resource(type='OS::Cinder::Volume',
                                        id='654321', name='name654')]
        fake_cntx = mock.MagicMock()

        result = self.pro_manager.list_protectable_dependents(
            fake_cntx, 'fake_id', 'OS::Nova::Server')
        self.assertEqual([{'type': 'OS::Cinder::Volume', 'id': '123456',
                           'name': 'name123'},
                          {'type': 'OS::Cinder::Volume', 'id': '654321',
                           'name': 'name654'}],
                         result)
