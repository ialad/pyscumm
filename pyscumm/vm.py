#    PySCUMM Engine. SCUMM based engine for Python
#    Copyright (C) 2006  PySCUMM Engine. http://pyscumm.org
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

#!/usr/bin/env python

"""
@author: Juan Jose Alonso Lara (KarlsBerg, jjalonso@pyscumm.org)
@author: Juan Carlos Rodrigo Garcia (Brainsucker, jrodrigo@pyscumm.org)
@since: 8/11/2006
"""

from types import NoneType
import pygame.event, base, driver, vector

class ChangeScene( Exception ):
    """
    Change the VM's activa escene. You can raise this
    exception anytime and give a new scene to the VM.
    raise ChangeScene( MyScene() ), the VM will take
    care of calling the scene stop and start method's.
    """
    def __init__( self, scene ):
        """
        Init's the ChangeScene exception, takes one
        parameter the new active Scene.
        @param scene: The VM's active scene
        @type scene: Scene
        """
        self._scene = scene

    def get_scene( self ):
        """
        Get the Scene.
        @return: Scene
        """
        return self._scene

    scene = property( get_scene )


class StopVM( Exception ):
    """This exception halts the VM, completely stopping it."""
    pass


class VM( base.StateMachine ):
    """
    VM (Virtual Machine) its a state machine (See state pattern), its the core of pyscumm,
    this haddle PyGame events, draw each drawable object depends of her Zplanes, etc
    This VM  recollect the low-level events (see main() method) and launch it to the active state
    in same method, update and draw each element of the game.

    PySCUMM have built-in some pre-mades VMStates..., the VMStates, are states of VM, these wants
    complex algorithms sometimes are unnecessary depending of the types of events that requires
    in your game on this momment.

    PySCUMM include pre-mades states:

            - vm.PassiveMode: This state ignores all events.
            - vm.NormalMode: This state launchs all events.
            - vm.KeyMode: This state only launchs keyboard.
            - vm.MouseMode: This state launches mouse events (click, double_click, drag, ...).
            - vm.DialogMode: This state only reports object clicked in the HUD.
    """
    # Singleton's shared state
    _shared_state = {}
    def __init__( self ):
        """Singletonize a VM object. Construct a Virtual Machine 
        with it's default components."""
        self.__dict__ = self._shared_state
        if self._shared_state: return
        base.StateMachine.__init__( self )
        self._mouse = driver.Mouse()
        self._display = driver.GLDisplay()
        self._clock = driver.Clock()
        self._scene = None

    def quit( self ):
        """Report to the active state a quit event."""
        self._state = self._state.on_quit()

    def keyboard_pressed( self, event ):
        """
        Report to the active state a keyboard key pressed.
        @param event: A Pygame KEYDOWN event
        @type event: Event(PyGame)
        """
        self._state = self._state.keyboard_pressed( event )

    def keyboard_released( self, event ):
        """
        Report to the active state a keyboard key pressed.
        @param event: A Pygame KEYUP event
        @type event: Event(PyGame)
        """
        self._state = self._state.keyboard_released( event )

    def mouse_pressed( self, event ):
        """
        Report to the active state a mouse button pressed.
        @param event: A Pygame MOUSEBUTTONDOWN event
        @type event: Event(Pygame)
        """
        self._state = self._state.mouse_pressed( event )

    def mouse_released( self, event ):
        """
        Report to the active state a mouse button released.
        @param event: A Pygame MOUSEBUTTONUP event
        @type event: Event(Pygame)
        """
        self._state = self._state.mouse_released( event )

    def update( self ):
        """Send an update message to the active scene."""
        self._state.update()

    def draw( self ):
        """Send an update message to the active scene."""
        self._state.draw()

    def start( self ):
        """Reset the VM with the vm.NormalMode state."""
        self._state = NormalMode()

    def main( self ):
        """
        Init the main loop of the engine, open a display window, launch events to the
        active state, update and render the scene each frame. if StopScene exception is launched,
        the VM stop self, and close the window.If however SceneChange exception is launched,
        the VM will reset single with the new scene data without close the window.
        """
        self.start()
        self._display.open()
        self._scene.start()
        leave = False
        while not leave:
            try:
                self._clock.tick()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.quit()
                    elif event.type == pygame.KEYDOWN:
                        self.keyboard_pressed( event )
                    elif event.type == pygame.KEYUP:
                        self.keyboard_released( event )
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self.mouse_pressed( event )
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.mouse_released( event )
                self.update()
                self.draw()
            except ChangeScene, e:
                self._scene.stop()
                self._scene = e.scene
                self._scene.start()
            except StopVM:
                leave = True
        self._display.close()

    def boot( self, scene, clock=None, display=None, mouse=None  ):
        """
        Boot a scene. Prepare a Virtual Machine and
        start running the main loop.
        @param scene: A Scene object
        @type scene: Scene
        @param clock: A Clock object
        @type clock: Clock
        @param display: A Display object
        @type display: Display
        @param mouse: A Mouse object
        @type mouse: Mouse
        """
        if not isinstance( clock, NoneType ): VM().clock = clock
        if not isinstance( display, NoneType ): VM().display = display
        if not isinstance( mouse, NoneType ): VM().mouse = mouse
        VM().scene = scene
        VM().main()

    def get_clock( self ):
        """
        Get the VM's clock.
        @return: A Clock object
        @rtype: Clock
        """
        return self._clock

    def set_clock( self, clock ):
        """
        Set the VM's clock.
        @param clock: A Clock object
        @type clock: Clock
        """
        self._clock = clock

    def get_display( self ):
        """
        Get the VM's display.
        @return: A Display object
        @rtype: Display
        """
        return self._display

    def set_display( self, display ):
        """
        Set the VM's display.
        @param display: A Display object
        @type display: Display
        """
        self._display = display

    def get_mouse( self ):
        """
        Get the VM's mouse.
        @return: A Mouse object
        @rtype: Mouse
        """
        return self._mouse

    def set_mouse( self, mouse ):
        """
        Set the VM's mouse.
        @param mouse: A Mouse object
        @type mouse: Mouse
        """
        self._mouse = mouse

    def get_scene( self ):
        """
        Get the VM's Scene.
        @return: A Scene object
        @rtype: Scene
        """
        return self._scene

    def set_scene( self, scene ):
        """
        Set the VM's Scene.
        @param scene: A Scene object
        @type scene: Scene
        """
        self._scene = scene

    scene   = property( get_scene, set_scene )
    mouse   = property( get_mouse, set_mouse )
    display = property( get_display, set_display )
    clock   = property( get_clock, set_clock )
    boot    = classmethod( boot )


class VMState( base.State ):
    """
    This class is a abstract state of the VM, the pre-mades modes of VM inherit from 
    this class. You can inherit it to write your own modes (states).
    VMState recieves the calls of the VM (Pygame events), transforms and process them to
    check if was a click, a doubleclick, a key pressed, key released, etc..., check if 
    the mouse collides with any object, and depending of the VMState setted on VM, 
    will launch high-level events to the scene instance.
    """

    def __init__( self ):
        """Build a VMState object."""
        base.State.__init__( self )

    def on_quit( self ):
        """Receives a quit request and forward it to the Scene."""
        VM().scene.on_quit()
        return self

    def keyboard_pressed( self, event ):
        """
        Receives a keyboard pressed event and forward it.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        VM().scene.on_key_down( event )
        return self

    def keyboard_released( self, event ):
        """
        Receives a keyboard released event and forward it.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        VM().scene.on_key_up( event )
        return self

    def mouse_pressed( self, event ):
        """
        Receives a mouse pressed event and forwards it.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        raise NotImplementedError

    def mouse_released( self, event ):
        """
        Receives a mouse released event and forwards it.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        raise NotImplementedError

    def update( self ):
        """Forward the update event to the Scene."""
        VM().scene.update()
        return self

    def draw( self ):
        """Forward the draw event to the Scene."""
        VM().scene.draw()
        return self


class NormalMode( VMState ):
    """
    NormalMode is a VM State that does picking (Mouse) related operations.
    It generates mouse_click, mouse_double_click, mouse_start_drag,
    mouse_end_drag and mouse_motion events.
    This class is a Singleton, so when setting the VM's active state you
    can program it like this:
        VM().state = NormalMode()
    """

    # Bit Flags
    BTN_PRESS_LEFT       = 1
    BTN_PRESS_CENTER     = 1<<1
    BTN_PRESS_RIGHT      = 1<<2
    BTN_CLICK_LEFT       = 1<<4
    BTN_CLICK_CENTER     = 1<<5
    BTN_CLICK_RIGHT      = 1<<6
    BTN_DBL_CLICK_LEFT   = 1<<8
    BTN_DBL_CLICK_CENTER = 1<<9
    BTN_DBL_CLICK_RIGHT  = 1<<10
    BTN_DRAG_LEFT        = 1<<12
    BTN_DRAG_CENTER      = 1<<13
    BTN_DRAG_RIGHT       = 1<<14

    # Button index, numbered as in Pygame's Events
    BTN_LEFT   = 1
    BTN_CENTER = 2
    BTN_RIGHT  = 3

    # Singleton's shared state
    _shared_state = {}

    def __init__( self ):
        """Singletonize a NormalMode object."""
        self.__dict__ = self._shared_state
        if self.__dict__: return
        VMState.__init__( self )
        self._flag = 0
        self._time = [ None ] * 4
        self._drag = [ None ] * 4
        self._loc  = vector.Vector3D()

    def mouse_pressed( self, event ):
        """
        Receives a mouse pressed from Pygame and activates the
        flag bits and sets the drag start locations if required.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        # Button pressed?
        if event.button == self.BTN_LEFT:
            # Set the pressed flag
            self._flag |= self.BTN_PRESS_LEFT
            # Record the current location of the mouse
            self._drag[ self.BTN_LEFT ] = VM().mouse.location
        elif event.button == self.BTN_CENTER:
            self._flag |= self.BTN_PRESS_CENTER
            self._drag[ self.BTN_CENTER ] = VM().mouse.location
        elif event.button == self.BTN_RIGHT:
            self._flag |= self.BTN_PRESS_RIGHT
            self._drag[ self.BTN_RIGHT ] = VM().mouse.location
        return self

    def mouse_released( self, event ):
        """
        Receives a mouse release from Pygame and deactivates the
        flag bits and resets the clicked timers if required.
        @param event: A Pygame event
        @type event: Event(Pygame)
        """
        if event.button == self.BTN_LEFT:
            # Unset the pressed bit
            self._flag &= ~self.BTN_PRESS_LEFT
            # Button clicked?
            if self._flag & self.BTN_CLICK_LEFT:
                # Then this is a double click
                self._flag &= ~self.BTN_CLICK_LEFT
                # ... set the double click flag, update() will take care of it
                self._flag |= self.BTN_DBL_CLICK_LEFT
            # The button is not clicked, this is the first click
            elif not ( self._flag & self.BTN_DRAG_LEFT ):
                # The user has clicked one time
                # set the flag bit
                self._flag |= self.BTN_CLICK_LEFT
                # Start the timer
                self._time[ self.BTN_LEFT ] = VM().clock.time
        elif event.button == self.BTN_CENTER:
            self._flag &= ~self.BTN_PRESS_CENTER
            if self._flag & self.BTN_CLICK_CENTER:
                self._flag &= ~self.BTN_CLICK_CENTER
                self._flag |= self.BTN_DBL_CLICK_CENTER
            elif not ( self._flag & self.BTN_DRAG_CENTER ):
                self._flag |= self.BTN_CLICK_CENTER
                self._time[ self.BTN_CENTER ] = VM().clock.time
        elif event.button == self.BTN_RIGHT:
            self._flag &= ~self.BTN_PRESS_RIGHT
            if self._flag & self.BTN_CLICK_RIGHT:
                self._flag &= ~self.BTN_CLICK_RIGHT
                self._flag |= self.BTN_DBL_CLICK_RIGHT
            elif not ( self._flag & self.BTN_DRAG_RIGHT ):
                self._flag |= self.BTN_CLICK_RIGHT
                self._time[ self.BTN_RIGHT ] = VM().clock.time
        return self

    def update( self ):
        """Here the flags, timers and start locations are checked 
        and acted upon their value. This method generates mouse_start_drag, 
        mouse_end_drag, mouse_click, mouse_double_click and mouse_motion
        events."""
        # Current mouse location
        location = VM().mouse.location
        d_drag   = VM().mouse.distance_drag
        t_click  = VM().mouse.time_double_click
        t        = VM().clock.time

        # Different position?
        if not ( location == self._loc ):
            # Send a mouse motion event
            VM().scene.on_mouse_motion( self._loc.clone() )
        # Update the mouse position
        self._loc = location

        # Left Button
        # Button double clicked?
        if self._flag & self.BTN_DBL_CLICK_LEFT:
            # Unset the double click flag
            self._flag &= ~self.BTN_DBL_CLICK_LEFT
            # ... send the event
            VM().scene.on_mouse_double_click( None, self.BTN_LEFT )
        # Button pressed?
        elif self._flag & self.BTN_PRESS_LEFT:
            # Mouse not dragging?, Start a drag? Only after distance_drag pixels moved
            if not ( self._flag & self.BTN_DRAG_LEFT ) \
            and ( ( self._drag[ self.BTN_LEFT ] - location ).length() > d_drag ):
                # Start dragging, set the drag bit
                self._flag |= self.BTN_DRAG_LEFT
                # ... launch the event
                VM().scene.on_mouse_drag_start( None, self.BTN_LEFT )
        # There is no button pressed, Is the mouse dragging?
        elif self._flag & self.BTN_DRAG_LEFT:
            # If it is stop dragging, unset the bit
            self._flag &= ~self.BTN_DRAG_LEFT
            # ... and send the event
            VM().scene.on_mouse_drag_end( self.BTN_LEFT )
        # There is no button pressed, was the button clicked?
        elif self._flag & self.BTN_CLICK_LEFT \
        and ( t - self._time[ self.BTN_LEFT ] ) > t_click:
            # If it is clicked and the double click timeout expired
            # unset the clicked bit
            self._flag &= ~self.BTN_CLICK_LEFT
            # ... and send the event
            VM().scene.on_mouse_click( None, self.BTN_LEFT )

        # Center Button
        if self._flag & self.BTN_DBL_CLICK_CENTER:
            self._flag &= ~self.BTN_DBL_CLICK_CENTER
            VM().scene.on_mouse_double_click( None, self.BTN_CENTER )
        elif self._flag & self.BTN_PRESS_CENTER:
            if not ( self._flag & self.BTN_DRAG_CENTER ) \
            and ( self._drag[ self.BTN_CENTER ] - location ).length() > d_drag:
                self._flag |= self.BTN_DRAG_CENTER
                VM().scene.on_mouse_drag_start( None, self.BTN_CENTER )
        elif self._flag & self.BTN_DRAG_CENTER:
            self._flag &= ~self.BTN_DRAG_CENTER
            VM().scene.on_mouse_drag_end( self.BTN_CENTER )
        elif self._flag & self.BTN_CLICK_CENTER \
        and ( t - self._time[ self.BTN_CENTER ] ) > t_click:
            self._flag &= ~self.BTN_CLICK_CENTER
            VM().scene.on_mouse_click( None, self.BTN_CENTER )

        # Right Button
        if self._flag & self.BTN_DBL_CLICK_RIGHT:
            self._flag &= ~self.BTN_DBL_CLICK_RIGHT
            VM().scene.on_mouse_double_click( None, self.BTN_RIGHT )
        elif self._flag & self.BTN_PRESS_RIGHT:
            if not ( self._flag & self.BTN_DRAG_RIGHT ) \
            and ( self._drag[ self.BTN_RIGHT ] - location ).length() > d_drag:
                self._flag |= self.BTN_DRAG_RIGHT
                VM().scene.on_mouse_drag_start( None, self.BTN_RIGHT )
        elif self._flag & self.BTN_DRAG_RIGHT:
            self._flag &= ~self.BTN_DRAG_RIGHT
            VM().scene.on_mouse_drag_end( self.BTN_RIGHT )
        elif self._flag & self.BTN_CLICK_RIGHT \
        and ( t - self._time[ self.BTN_RIGHT ] ) > t_click:
            self._flag &= ~self.BTN_CLICK_RIGHT
            VM().scene.on_mouse_click( None, self.BTN_RIGHT )

        return VMState.update( self )

class PassiveMode( VMState ):
    """
    This state of the VM, ignores all the PyGame events, it gets the
    events and does nothing with them.
    PassiveMode is the best VMState state, for game-intros, movie-modes and
    other situations where your scene does not require events.
    """
    # Singleton's shared state
    _shared_state = {}

    def __init__( self ):
        """Singletonize a PassiveMode object."""
        self.__init__ = self._shared_state
        if self.__init__: return
        VMState.__init__( self )

    def keyboard_pressed( self, event ):
        """
        Ignores this event.
        @param event: A Pygame KEYDOWN event
        @type event: Event(Pygame)
        @return: This object
        @rtype: PassiveMode
        """
        return self

    def keyboard_released( self, event ):
        """
        Ignores this event.
        @param event: A Pygame KEYUP event
        @type event: Event(Pygame)
        @return: This object
        @rtype: PassiveMode
        """
        return self

    def mouse_pressed( self, event ):
        """
        Ignores this event.
        @param event: A Pygame MOUSEBUTTONDOWN event
        @type event: Event(Pygame)
        @return: This object
        @rtype: PassiveMode
        """
        return self

    def mouse_released( self, event ):
        """
        Ignores this event.
        @param event: A Pygame MOUSEBUTTONUP event
        @type event: Event(Pygame)
        @return: This object
        @rtype: PassiveMode
        """
        return self


class KeyMode( VMState ):
    """
    This state of the VM, ignores all events except when coming from the 
    keyboard. KeyMode is the best VMState option when your scene needs to 
    ignore all but the keyboard events.
    """
    # Singleton's shared state
    _shared_state = {}

    def __init__( self ):
        """Singletonize a KeyMode object."""
        self.__init__ = self._shared_state
        if self.__init__: return
        VMState.__init__( self )

    def mouse_pressed( self, event ):
        """
        Ignore this event.
        @param event: A Pygame MOUSEBUTTONDOWN event
        @type event: Event(Pygame)
        @return: This object
        @rtype: KeyMode
        """
        return self

    def mouse_released( self, event ):
        """
        Ignore this event.
        @param event: A Pygame MOUSEBUTTONUP event
        @type event: Event(Pygame)
        @return: This object
        @rtype: KeyMode
        """
        return self



class MouseMode( NormalMode ):
    """
    This mode (state) of the VM, generates mouse events ignoring the 
    keyboard ones. MouseMode is the best VM state when your 
    scene requires mouse events only.
    """
    _shared_state = {}

    def __init__( self ):
        """Singletonize a MouseMode object.""" 
        self.__init__ = self._shared_state
        if self.__init__: return
        NormalMode.__init__( self )

    def keyboard_pressed( self, event ):
        """
        Ignore this event.
        @param event: A Pygame KEYDOWN event
        @type event: Event(Pygame)
        @return: This object
        @rtype: MouseMode
        """
        return self

    def keyboard_released( self, event ):
        """
        Ignore this event.
        @param event: A PyGame KEYUP event
        @type event: Event(Pygame)
        @return: This object
        @rtype: MouseMode
        """
        return self


class DialogMode( MouseMode ):
    """
    On this state, the mouse only collides with the visual elements of the
    dialog interface (HUD) and ignores all the other objects...
    The HUD is the class that handdle the visual interface of the dialogs.
    MouseMode is the best VM state when your scene is undergoing a dialog
    between actors.
    """
    pass
