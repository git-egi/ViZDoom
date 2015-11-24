#include "ViziaMain.h"
#include <iostream>
#include <vector>
#include <Python.h>

#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>

#include <boost/python/list.hpp>
#include <boost/python/object.hpp>
#include <boost/python/tuple.hpp>

using boost::python::tuple;

using boost::python::api::object;

#define PY_NONE object()

/* C++ code that wraps ViziaMain with python object */

/* isn't it a good idea just to extend ViziaMain?*/
class ViziaPythonApi{
	
    public:
        ViziaPythonApi(){
            this->main=new ViziaMain();
            import_array();
        }
        ~ViziaPythonApi(){
            this->main->close();
            delete(this->main);
        }

        void loadConfig(std::string file){this->main->loadConfig(file);}
        void init()
        {
            bool init_success = (this->main->init() == 0);
            /* fill state format */
            if (init_success)
            {
                ViziaMain::StateFormat cpp_format = this->main->getStateFormat();
                boost::python::list image_shape;
                int image_shape_len = 3;
                for (int i = 0; i <image_shape_len; ++i) {
                    image_shape.append(cpp_format.image_shape[i]);
                }
                this->state_format = boost::python::make_tuple(tuple(image_shape),cpp_format.var_len);
            }
        }
        void close(){this->main->close();}

        void newEpisode(){this->main->newEpisode();}
    	float makeAction(boost::python::list action_list){
    		int list_length = boost::python::len(action_list);
    		std::vector<bool> action = std::vector<bool>(list_length);
    		for (int i=0; i<list_length; i++)
    		{
    			action[i]=boost::python::extract<bool>(action_list[i]);
    		}
    		return this->main->makeAction(action);
    	}
        tuple getState(){
            ViziaMain::State state = this->main->getState();
            //TODO convert the image state to numpy array
            if (state.vars != NULL)
            {
                //TODO convert misc vector to numpy array
                return boost::python::make_tuple(state.number, PY_NONE,PY_NONE);
            }
            else
            {
                return boost::python::make_tuple(state.number, PY_NONE);
            }
            
        }

        tuple getStateFormat(){
           return this->state_format;
        }
        int getActionFormat(){return this->main->getActionFormat();}
        bool isNewEpisode(){return this->main->isNewEpisode();}
        bool isEpisodeFinished(){ return this->main->isEpisodeFinished();}
       
        /* not sure if we need this */
        object getLastAction(){
            //TODO
            return PY_NONE;
        }
        /* Pre init methods */
        void addAvailableKey(int key){this->main->addAvailableKey(key);}
        void addAvailableKey(std::string key){this->main->addAvailableKey(key);}
        void addStateAvailableVar(int var){this->main->addStateAvailableVar(var);}
        void addStateAvailableVar(std::string var){this->main->addStateAvailableVar(var);}

        void setDoomGamePath(std::string path){this->main->setDoomGamePath(path);}
        void setDoomIwadPath(std::string path){this->main->setDoomIwadPath(path);}
        void setDoomFilePath(std::string path){this->main->setDoomFilePath(path);}
        void setDoomMap(std::string map){this->main->setDoomMap(map);}
        void setDoomSkill(int skill){this->main->setDoomSkill(skill);}
        void setDoomConfigPath(std::string path){this->main->setDoomConfigPath(path);}

        void setNewEpisodeOnTimeout(bool set){this->main->setNewEpisodeOnTimeout(set);}
        void setNewEpisodeOnPlayerDeath(bool set){this->main->setNewEpisodeOnPlayerDeath(set);}
        void setEpisodeTimeoutInMiliseconds(unsigned int ms){this->main->setEpisodeTimeoutInMiliseconds(ms);}
        void setEpisodeTimeoutInDoomTics(unsigned int tics){this->main->setEpisodeTimeoutInDoomTics(tics);}

        void setScreenResolution(int width, int height){this->main->setScreenResolution(width,height);}
        void setScreenWidth(int width){this->main->setScreenWidth(width);}
        void setScreenHeight(int height){this->main->setScreenHeight(height);}
        void setScreenFormat(int format){this->main->setScreenFormat(format);}
        void setRenderHud(bool hud){this->main->setRenderHud(hud);}
        void setRenderWeapon(bool weapon){this->main->setRenderWeapon(weapon);}
        void setRenderCrosshair(bool crosshair){this->main->setRenderCrosshair(crosshair);}
        void setRenderDecals(bool decals){this->main->setRenderDecals(decals);}
        void setRenderParticles(bool particles){this->main->setRenderParticles(particles);}

        int getScreenWidth(){return this->main->getScreenWidth();}
        int getScreenHeight(){return this->main->getScreenHeight();}
        int getScreenPitch(){return this->main->getScreenPitch();}
        int getScreenSize(){return this->main->getScreenSize();}
        int getScreenFormat(){return this->main->getScreenFormat();}

        /* why should we need this? */
        const ViziaDoomController* getController(){return this->main->getController();}
        

    private:

        ViziaMain * main;
        tuple state_format;

};
