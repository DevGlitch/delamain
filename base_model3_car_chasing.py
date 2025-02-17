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
import pygame
import argparse
import numpy as np
import cv2

from base.hud import HUD
from base.world import World
from base.manual_control import KeyboardControl
from lane_tracking.util.carla_util import CarlaSyncMode
from base.debug_cam import debug_view, save_img

from lane_tracking.cores.control.pure_pursuit import PurePursuitPlusPID
from lane_tracking.lane_track import lane_track_init, get_trajectory_from_lane_detector, get_speed, send_control
from lane_tracking.dgmd_track import image_pipeline

from car_chasing.car_chasing_agent import chasing_car_init, agent_init
from car_chasing.car_chasing_controller import ChaseControl


# ==============================================================================
# -- Car Chasing Configuration Variables ---------------------------------------
# ==============================================================================
optimalDistance = 8
nOfFramesToSkip = 0
extrapolate = True
behaviour_planner_frequency_divisor = 2
y_offset = 10

# For object avoidance
obsticle_vehicleSpawned = False

# ==============================================================================
# -- Car Chasing Global Objects ---------------------------------------
# ==============================================================================
# Add ChaseControl, should be initalized outside the game loop for efficiency 
chaseControl = ChaseControl(optimalDistance=optimalDistance, nOfFramesToSkip=nOfFramesToSkip, extrapolate=extrapolate, behaviour_planner_frequency_divisor=behaviour_planner_frequency_divisor)



# ==============================================================================
# -- game_loop() ---------------------------------------------------------------
# ==============================================================================


def game_loop(args):
    pygame.init()
    pygame.font.init()
    world = None

    try:
        client = carla.Client("localhost", 2000)
        client.set_timeout(100.0)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height)
        test_map = client.load_world('Town03')
        world = World(test_map, hud, args)
        controller = KeyboardControl(world, False)

        actor_list = []
        sensors = []

        # ==================================================================
        a_controller = PurePursuitPlusPID()
        cg, ld = lane_track_init()


        # ======================= Car Chasing Objects ========================
        #  Add trailing vehicle
        # TODO Set trailing posisiton. By default it is set to be relative to world.player
        trailing_vehicle = chasing_car_init(world=world, position=None, y_offset=y_offset)
        actor_list.append(trailing_vehicle)

        # TODO - add sensors
        blueprint_library = world.world.get_blueprint_library()

        # Camera RGB sensor
        bp_cam_rgb = blueprint_library.find('sensor.camera.rgb')
        bp_cam_rgb.set_attribute('image_size_x', str(cg.image_width))
        bp_cam_rgb.set_attribute('image_size_y', str(cg.image_height))
        bp_cam_rgb.set_attribute('fov', str(cg.field_of_view_deg))

        # Semantic Segmentation camera
        bp_cam_seg = blueprint_library.find('sensor.camera.semantic_segmentation')
        bp_cam_seg.set_attribute('image_size_x', str(cg.image_width))
        bp_cam_seg.set_attribute('image_size_y', str(cg.image_height))
        bp_cam_seg.set_attribute('fov', str(cg.field_of_view_deg))

        # Spawn Sensors
        transform = carla.Transform(carla.Location(x=0.7, z=cg.height), carla.Rotation(pitch=-1*cg.pitch_deg))
        cam_rgb = world.world.spawn_actor(bp_cam_rgb, transform, attach_to=world.player)
        print('created %s' % cam_rgb.type_id)
        cam_seg = world.world.spawn_actor(bp_cam_seg, transform, attach_to=world.player)
        print('created %s' % cam_seg.type_id)

        # Append actors / may not be necessary
        actor_list.append(cam_rgb)
        actor_list.append(cam_seg)
        sensors.append(cam_rgb)
        sensors.append(cam_seg)
        # ==================================================================


        # --- Adding sensors to trailing_vehicle
        # Adding RGB camera
        trail_cam_rgb_blueprint = world.world.get_blueprint_library().find('sensor.camera.rgb')
        trail_cam_rgb_blueprint.set_attribute('fov', '90')
        trail_cam_rgb = world.world.spawn_actor(
           trail_cam_rgb_blueprint,
            carla.Transform(carla.Location(x=1.5, z=1.4,y=0.3), carla.Rotation(pitch=0)),
            attach_to=trailing_vehicle)
        actor_list.append(trail_cam_rgb)
        sensors.append(trail_cam_rgb)

        # Adding Segmentation camera
        trail_cam_seg = world.world.spawn_actor(
            blueprint_library.find('sensor.camera.semantic_segmentation'),
            carla.Transform(carla.Location(x=1.5, z=1.4,y=0), carla.Rotation(pitch=0)), #5,3,0 # -0.3
            attach_to=trailing_vehicle)
        actor_list.append(trail_cam_seg)
        sensors.append(trail_cam_seg)
       
        # ==================================================================
        frame = 0 
        FPS = 30
        speed, traj = 0, np.array([])
        time_cycle, cycles = 0.0, 30
        clock = pygame.time.Clock()
        # TODO - add sensor to SyncMode
        with CarlaSyncMode(world.world, *sensors, fps=FPS) as sync_mode:
            while True:
                clock.tick_busy_loop(FPS)
                time_cycle += clock.get_time()
                if controller.parse_events(client, world, clock):
                    return
                # Advance the simulation and wait for the data.
                tick_response = sync_mode.tick(timeout=2.0)
                
                # Data retrieval
                snapshot, image_rgb, image_seg, trailing_image_rgb, trailing_image_seg = tick_response


                # ======================= Car Chasing Section =========================
                trailing_steer, trailing_throttle, real_dist = chaseControl.behaviour_planner(leading_vehicle=world.player, 
                                                                                    trailing_vehicle=trailing_vehicle, 
                                                                                    trailing_image_seg=trailing_image_seg, 
                                                                                    trail_cam_rgb=trail_cam_rgb,
                                                                                    frame=frame)
                
                send_control(trailing_vehicle, trailing_throttle, trailing_steer, 0)

                # ==================================================================


                if time_cycle >= 1000.0/cycles:
                    time_cycle = 0.0

                    image_seg.convert(carla.ColorConverter.CityScapesPalette)
                    # ==================================================================
                    # TODO - run features
                    try:
                        traj, lane_mask = get_trajectory_from_lane_detector(ld, image_seg) # stay in lane
                        # dgmd_mask = image_pipeline(image_seg)
                        # save_img(image_seg)
                        print(traj.shape, traj)
                    except:
                        continue
                    # ==================================================================
                    # TODO - features init/ module
                    # Debug data
                    # debug_view(image_rgb, image_seg, lane_mask)
                    # debug_view(image_rgb, image_seg)
                    # cv2.imshow("debug view", dgmd_mask)
                    # cv2.waitKey(1)

                # PID Control
                if traj.any():
                    speed = get_speed(world.player)
                    throttle, steer = a_controller.get_control(traj, speed, desired_speed=15, dt=1./FPS)
                    send_control(world.player, throttle, steer, 0)

                world.tick(clock)
                world.render(display)
                pygame.display.flip()

                frame +=1
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
