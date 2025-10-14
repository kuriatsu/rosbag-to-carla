#!/usr/bin/env python

# Copyright (c) 2019 Aptiv
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys

try:
    sys.path.append(glob.glob('**/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================

import carla
import weakref
import argparse
import collections
import math
import logging
import datetime

try:
    import pygame
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

VIEW_FOV = 100

# data log
logging.basicConfig(filename='/home/kuriatsu/Documents/carla_driving_result/time_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.log', level=logging.INFO)
logging.info('round,time,collision')
# ==============================================================================
# -- Cliant ----------------------------------------------------
# ==============================================================================


class Cliant(object):
    """
    Basic implementation of a synchronous client.
    """

    def __init__(self, args):
        self.client = None
        self.world = None
        self.display = None
        self.image = None
        self.capture = True
        self.camera = None


    def set_synchronous_mode(self, synchronous_mode):
        """
        Sets synchronous mode.
        """

        settings = self.world.get_settings()
        settings.synchronous_mode = synchronous_mode
        self.world.apply_settings(settings)

    def game_loop(self, args):
        """
        Main program loop.
        """

        pygame.init()

        self.client = carla.Client(args.host, args.port)
        self.client.set_timeout(2.0)
        self.world = self.client.get_world()

        self.camera = Camera(args, self.world)

        self.display = pygame.display.set_mode(args.res, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame_clock = pygame.time.Clock()

        self.set_synchronous_mode(True)

        while True:
            self.world.tick()
            pygame_clock.tick(20)

            self.camera.render(self.display)
            pygame.display.flip()
            pygame.event.pump()

        pygame.quit()

# ==============================================================================
# -- Camera --------------------------------------------------------------------
# ==============================================================================

class Camera(object):
    def __init__(self, args, world):
        self.camera = None
        self.image = None
        self.capture = False
        self.spawned_here=False
        # self.camera_tran = carla.Transform(carla.Location(-0.05,-0.2,1.31), carla.Rotation(0.0,0.0,0.0))
        self.camera_tran = carla.Transform(carla.Location(-0.05,-0.2,50), carla.Rotation(-90.0,0.0,90.0))

        for carla_actor in world.get_actors():
            if carla_actor.type_id == "sensor.camera.rgb":
                if carla_actor.attributes.get('role_name') == args.cameraname:
                    self.camera = carla_actor
                    print('found camera')

        if self.camera is None:
            self.camera = self.set_sensor(args, world)
            self.spawned_here = True

        weak_self = weakref.ref(self)
        self.camera.listen(lambda image: weak_self().set_image(weak_self, image))

        calibration = np.identity(3)
        calibration[0, 2] = args.res[0] / 2.0
        calibration[1, 2] = args.res[1] / 2.0
        calibration[0, 0] = calibration[1, 1] = args.res[0] / (2.0 * np.tan(VIEW_FOV * np.pi / 360.0))
        self.camera.calibration = calibration

    @staticmethod
    def set_image(weak_self, img):
        """
        Sets image coming from camera sensor.
        The self.capture flag is a mean of synchronization - once the flag is
        set, next coming image will be stored.
        """
        self = weak_self()
        if self.capture:
            self.capture = False
            self.image = img

    def render(self, display):
        """
        Transforms image from camera sensor and blits it to main pygame display.
        """
        self.capture = True

        if self.image is not None:
            array = np.frombuffer(self.image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (self.image.height, self.image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            display.blit(surface, (0, 0))

    def set_sensor(self, args, world):
        """set sensor if specified sensor is not in world

        """
        ego_vehicle = None
        for carla_actor in world.get_actors():
            if carla_actor.attributes.get('role_name') == args.egoname:
                ego_vehicle = carla_actor

        if ego_vehicle is None:
            exit()

        camera_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(args.res[0]))
        camera_bp.set_attribute('image_size_y', str(args.res[1]))
        camera_bp.set_attribute('role_name', args.cameraname)
        camera_transform = carla.Transform(carla.Location(x=0.0, y=0.0, z=0.0), carla.Rotation(0.0,0.0,0.0))
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=ego_vehicle, attachment_type=carla.AttachmentType.SpringArm)

        camera.set_transform(self.camera_tran)
        return camera

# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    """
    Initializes the client-side bounding box demo.
    """
    parser_position = lambda x: list(map(float, x.split(',')))
    parser_res = lambda x: tuple(map(int, x.split('x')))

    argparser = argparse.ArgumentParser(
        description='Carla image viewer for demo')
    argparser.add_argument(
        '--host',
        default='127.0.0.1',
        help='IP of the host server (127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-c', '--cameraname',
        metavar='NAME',
        default='wide_front',
        help='camera role name (default: "wide_front")')
    argparser.add_argument(
        '--res',
        metavar='WIDTHxHEIGHT',
        default='800x600',
        type=parser_res,
        help='window resolution (default: 3840x1080)')
    argparser.add_argument(
        '-e', '--egoname',
        metavar='NAME',
        default='ego_vehicle',
        help='vehicle role name (default: "ego_vehicle")')

    args, unknown = argparser.parse_known_args()

    try:
        client = Cliant(args)
        client.game_loop(args)
    finally:
        client.set_synchronous_mode(False)
        print('destroy camera')
        client.camera.camera.destroy()

        # if self.camera.spawned_here:
        print('EXIT')


if __name__ == '__main__':
    main()

