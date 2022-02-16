#!/usr/bin/env python3

import os
from random import choice
from time import sleep
import cv2
import vizdoom as vzd
import numpy as np
import math

# In this example I'm working on the map defend the line
DEFAULT_CONFIG = os.path.join(vzd.scenarios_path, "defend_the_line.cfg")

# I created this list to set names of objects that I don't want my agent to focus
# The reason is, if agent focuses these objects he doesn't work at all or he doesn't work as expected
# For example I don't want the agent to focus the main player, I want him to focus enemy objects
not_intersted = ["DoomPlayer","DoomImpBall"]

# This function performs the player action based on the closest object
# If the closest object's y position is in range of shooting then shoot
# In any other case move right or left based if the y position value is bigger or less

def getAction(g,obj,s):
    if(abs(s[1]-obj.object_position_y) <= 1.5):
        g.make_action(Movement_Map["SHOOT"])
    elif(s[1] > obj.object_position_y):
        g.make_action(Movement_Map["MOV_RIGHT"])
    elif(s[1] < obj.object_position_y):
        g.make_action(Movement_Map["MOV_LEFT"])

def getDir(st,co):
    pxpos = st.game_variables[0]
    pypos = st.game_variables[1]
    oxpos = co.object_position_x
    oypos = co.object_position_y
    lxpos = pxpos + 400
    lypos = pypos
    dir = (oxpos-pxpos)*(lypos-pypos) - (oypos-pypos)*(lxpos-pxpos)
    if(dir<0):
        return "Left"
    elif(dir>0):
        return "Right"
    else:
        return "Same"

#Below I created a function that computes the 3D Distance between two objects
#In my case the Player Object and the Enemy Objects
#The Formula I use is : distance = squared root of ( (enemy x - player x)^2 + (enemy y - player y)^2 + (enemy z - player z)^2 )
def getClosestObject(st):
    retObject = None
    retArray = None
    minDist = float('inf')
    pxpos = st.game_variables[0]
    pypos = st.game_variables[1]
    pzpos = st.game_variables[2]
    for l in st.labels:
       oxpos = l.object_position_x
       oypos = l.object_position_y
       ozpos = l.object_position_z
       dist = math.sqrt(pow(oxpos-pxpos,2)+pow(oypos-pypos,2)+np.power(ozpos-pzpos,2))
       if(dist<minDist):
           obj_name = (l.object_name).strip()
           if(obj_name not in not_intersted):
               minDist = dist
               retObject = l
               dir = getDir(st,retObject)
               retArray = [retObject,minDist,dir]
    if(retArray is not None):
        return retArray

def draw_bounding_box(buffer, x, y, width, height, color):
    for i in range(width):
        buffer[y, x + i, :] = color
        buffer[y + height, x + i, :] = color
    for i in range(height):
        buffer[y + i, x, :] = color
        buffer[y + i, x + width, :] = color

def color_labels(labels):
    tmp = np.stack([labels] * 3, -1)
    tmp[labels == 0] = [255, 0, 0]
    tmp[labels == 1] = [0, 0, 255]
    return tmp

def setupui(game):
    game.set_render_hud(False)
    game.set_render_minimal_hud(False)  
    game.set_render_crosshair(False)
    game.set_render_weapon(True)
    game.set_render_decals(False)
    game.set_render_particles(False)
    game.set_render_effects_sprites(False)
    game.set_render_messages(False)
    game.set_render_corpses(False)
    game.set_render_screen_flashes(False)

if __name__ == "__main__":
    
    game = vzd.DoomGame()
    game.load_config(DEFAULT_CONFIG)

    #----------------------------------------------------------------------
    #                         SETUP SCREEN MODES
    #----------------------------------------------------------------------

    game.set_screen_resolution(vzd.ScreenResolution.RES_640X480)
    game.set_screen_format(vzd.ScreenFormat.RGB24)

    #----------------------------------------------------------------------
    #                           SETUP BUFFERS
    #----------------------------------------------------------------------
    game.set_depth_buffer_enabled(True)
    game.set_labels_buffer_enabled(True)
    game.set_automap_buffer_enabled(True)
    game.set_objects_info_enabled(True)
    game.set_sectors_info_enabled(True)
    game.set_automap_buffer_enabled(True)
    game.set_automap_mode(vzd.AutomapMode.OBJECTS_WITH_SIZE)
    game.add_game_args("+viz_am_center 1")
    game.add_game_args("+am_backcolor 000000")
    
    game.clear_available_game_variables()
    game.add_available_game_variable(vzd.GameVariable.POSITION_X)
    game.add_available_game_variable(vzd.GameVariable.POSITION_Y)
    game.add_available_game_variable(vzd.GameVariable.POSITION_Z)
    game.add_available_game_variable(vzd.GameVariable.ANGLE)

    #----------------------------------------------------------------------
    #               SETUP GUI ENABLES/DISABLES UI OBJECTS
    #----------------------------------------------------------------------

    setupui(game)

    #----------------------------------------------------------------------
    #                           BUTTON SETUP
    #----------------------------------------------------------------------
    avail_buttons = [vzd.TURN_LEFT ,vzd.TURN_RIGHT ,vzd.MOVE_BACKWARD, vzd.MOVE_FORWARD, vzd.Button.MOVE_LEFT, vzd.Button.MOVE_RIGHT, vzd.Button.ATTACK]
    
    Movement_Map = {
        "T_LEFT"           : [1, 0, 0, 0, 0, 0, 0],
        "T_RIGHT"          : [0, 1, 0, 0, 0, 0, 0],
        "MOV_BACK"         : [0, 0, 1, 0, 0, 0, 0],
        "MOV_FOR"          : [0, 0, 0, 1, 0, 0, 0],
        "MOV_LEFT"         : [0, 0, 0, 0, 1, 0, 0],
        "MOV_RIGHT"        : [0, 0, 0, 0, 0, 1, 0],
        "SHOOT"            : [0, 0, 0, 0, 0, 0, 1],
        "MOV_FOR_LEFT"     : [0, 0, 0, 1, 1, 0, 0],
        "MOV_FOR_RIGHT"    : [0, 0, 0, 1, 0, 1, 0],
        "T_MOV_RIGHT"      : [0, 1, 0, 0, 0, 1, 0],
        "T_MOV_LEFT"       : [1, 0, 0, 0, 1, 0, 0]
    }

    game.set_available_buttons(avail_buttons)

    #----------------------------------------------------------------------
    #                       EPISODE SETTINGS
    #----------------------------------------------------------------------
    game.set_episode_start_time(10)
    episodes = 10
    #----------------------------------------------------------------------

    game.set_mode(vzd.Mode.PLAYER)
    game.init()

    #----------------------------------------------------------------------
    #                       ENGINE SLEEP TIME SET
    #----------------------------------------------------------------------
    sleep_time = 20
    #----------------------------------------------------------------------


    BLUE_COLOR = [203, 0, 0]
    RED_COLOR  = [0, 0, 203]

    for i in range(episodes):
        game.new_episode()
        while not game.is_episode_finished():

            state = game.get_state()

            screen = state.screen_buffer
            cv2.imshow('Screen Buffer', screen)

            labels = state.labels_buffer
            if labels is not None:
                cv2.imshow('ViZDoom Label Buffer', color_labels(labels))
           
            map = state.automap_buffer
            if map is not None:
                cv2.imshow('ViZDoom Automap Buffer', map)

            for l in state.labels:
                draw_bounding_box(screen, l.x, l.y, l.width, l.height, RED_COLOR)
            
            cv2.waitKey(sleep_time)

            print("---------------------------------------")
            print("                 PLAYER                ")
            print("---------------------------------------")
            print("X Pos\tY Pos\tZ Pos\tAngle")
            p_xpos = round(state.game_variables[0],2)
            p_ypos = round(state.game_variables[1],2)
            p_zpos = round(state.game_variables[2],2)
            p_angle = round(state.game_variables[3],2)
            print(str(p_xpos)+"\t"+str(p_ypos)+"\t"+str(p_zpos)+"\t"+str(p_angle))

            closest_object_data = getClosestObject(state)

            closest_object = closest_object_data[0]
            closest_object_distance = closest_object_data[1]
            closest_object_dir = closest_object_data[2]

            if(closest_object is not None):
                name = closest_object.object_name
                xpos = closest_object.object_position_x
                ypos = closest_object.object_position_y
                zpos = closest_object.object_position_z
                print("---------------------------------------")
                print("             CLOSEST OBJECT            ")
                print("           (Distance = "+str(round(closest_object_distance,2))+")")
                print("---------------------------------------")
                print("Name -> "+str(name))
                print("X Pos\tY Pos\tZ Pos\tDirection")
                print(str(round(xpos,2))+"\t"+str(round(ypos,2))+"\t"+str(round(zpos,2))+"\t"+closest_object_dir)

                # #Perform an action based on the closest object to the player 
                getAction(game,closest_object,state.game_variables)

    # It will be done automatically anyway but sometimes you need to do it in the middle of the program...
    cv2.destroyAllWindows()

    game.close()
