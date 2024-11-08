import asyncio
from dotenv import load_dotenv
import os
from typing import Any, ClassVar, Final, Mapping, Optional, Sequence

from typing_extensions import Self
from viam.components.sensor import *
from viam.module.module import Module
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.easy_resource import EasyResource
from viam.resource.types import Model, ModelFamily
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from viam.utils import SensorReading


class TestSensor(Sensor, EasyResource):
    MODEL: ClassVar[Model] = Model(
        ModelFamily("bradgrigsby", "se-interview"), "test-sensor"
    )

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        """This method creates a new instance of this Sensor component.
        The default implementation sets the name from the `config` parameter and then calls `reconfigure`.

        Args:
            config (ComponentConfig): The configuration for this resource
            dependencies (Mapping[ResourceName, ResourceBase]): The dependencies (both implicit and explicit)

        Returns:
            Self: The resource
        """
        return super().new(config, dependencies)

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        """This method allows you to validate the configuration object received from the machine,
        as well as to return any implicit dependencies based on that `config`.

        Args:
            config (ComponentConfig): The configuration for this resource

        Returns:
            Sequence[str]: A list of implicit dependencies
        """
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        """This method allows you to dynamically update your service when it receives a new `config` object.

        Args:
            config (ComponentConfig): The new configuration
            dependencies (Mapping[ResourceName, ResourceBase]): Any dependencies (both implicit and explicit)
        """
        return super().reconfigure(config, dependencies)

    async def connect(self):
        load_dotenv()
        opts = RobotClient.Options.with_api_key(
            api_key=os.getenv("API_KEY"),
            api_key_id=os.getenv("API_KEY_ID")
        )
        return await RobotClient.at_address(os.getenv("ADDRESS"), opts)

    async def get_readings(
        self,
        *,
        extra: Optional[Mapping[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Mapping[str, SensorReading]:
        machine = await self.connect()

        # Setup vision service
        people_detector = VisionClient.from_robot(machine, "peopleDetector")

        # Collect detections
        detections = await people_detector.get_detections_from_camera("camera-1")

        # Find detections with class name == "person" and condidence >= 0.8
        person_detected = 0
        for detection in detections:
            if detection.class_name.lower() == "person" and detection.confidence >= 0.8:
                person_detected = 1

        return {
            "person_detected": person_detected
        }


if __name__ == "__main__":
    asyncio.run(Module.run_from_registry())

