import glob
import os
import sys

try:
    sys.path.append(glob.glob('carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================

import carla
import argparse
import pygame

from base.hud import HUD
from base.world import World
from base.manual_control import KeyboardControl
from base.debug_cam import process_img

from lane_tracking.cores.control.pure_pursuit import PurePursuitPlusPID
from lane_tracking.lane_track2 import lane_track_init
from lane_tracking.util.carla_util import CarlaSyncMode, should_quit, draw_image


# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================

def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(10.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height)
        test_map = client.load_world('Town04')
        world = World(test_map, hud, args)
        m_controller = KeyboardControl(world, False)

        # ======================================================================
        actor_list = []
        sensors = []

        #TODO - features init/misc
        a_controller = PurePursuitPlusPID()
        cg, ld = lane_track_init()

        #TODO - add sensors
        blueprint_library = world.world.get_blueprint_library()

        # Camera RGB sensor
        bp_cam_rgb = blueprint_library.find('sensor.camera.rgb')
        bp_cam_rgb.set_attribute('image_size_x', '1024')
        bp_cam_rgb.set_attribute('image_size_y', '512')
        bp_cam_rgb.set_attribute('fov', '110')
        bp_cam_rgb.set_attribute('sensor_tick', '0.0')

        # Spawn Sensors
        transform = carla.Transform(carla.Location(x=0.5, z=cg.height), carla.Rotation(pitch=-1*cg.pitch_deg))
        cam_rgb = world.world.spawn_actor(bp_cam_rgb, transform, attach_to=world.player)
        print('created %s' % cam_rgb.type_id)

        # Append actors
        actor_list.append(cam_rgb)
        sensors.append(cam_rgb)

        # Activate Sensors
        # cam_rgb.listen(lambda data: process_img(data))
        # ======================================================================

        clock = pygame.time.Clock()
        while True:
            if should_quit():
                return
            # clock.tick()
            clock.tick_busy_loop(60)
            if m_controller.parse_events(client, world, clock):
                return
            # ==================================================================
            # TODO - run features


            # ==================================================================

            world.tick(clock)
            world.render(display)
            pygame.display.flip()
    finally:
        if (world and world.recording_enabled):
            client.stop_recorder()

        if world is not None:
            world.destroy()
        pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    argparser = argparse.ArgumentParser(
        description='Base Model Environment')
    args = argparser.parse_args()
    args.width, args.height = [1280, 720]

    try:
        game_loop(args)
    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')

if __name__ == '__main__':
    main()
