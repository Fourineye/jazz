# Engine
This project is to wrap pygame into a more conveinent format that handles some of the more common tasks in game development.

## #TODO
- Name engine
- Create parenting system
- Redo UI module
- Create documentation

## Completed
- Basic application structure
- Collision
- Input wrapping / event handling
- Basic UI module

# Documentation
## engine.py
### Application
- width: width of the game window in pixels
- height: height of the game window in pixels
- name(optional): String to be displayed on the toolbar of the game window
- fps_max(optional): max fps at which the game will update
- flags(optional): pygame display tags to be passed to the display 

This is the base class that the entire engine runs on. Once this is initialized you will need to add scenes to it to actually run anything.
The first scene added to the instance will be the one to run when the application is started.
#### Methods
##### add_scene
- scene: reference to a child of the Scene class.

This method adds a scene to the application without initializing it, if it is the first scene added it will be set as the next scene.
##### run
This method starts the starts the game loop, loads the first scene and handles loading and unloading scenes 
##### stop
This method stops the application. Telling the active scene to finish and then leaving the game loop.
##### set_next_scene
- name: name of the scene to load as defined in the scene class.

This method sets the scene to load when the current scene finishes, raises an exception if you pass a name that was not added to the instance.
