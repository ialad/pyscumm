import pyscumm, sys, random, pyscumm.box

class MyObject( pyscumm.object.Object ):

    def __init__( self ):
        self[ 'box' ] = pyscumm.box.Box()
        self[ 'box' ].location[0] = 320.; self[ 'box' ].location[1] = 240.
        self[ 'box' ].box[0][0] = -200.; self[ 'box' ].box[0][1] = -200.
        self[ 'box' ].box[1][0] =  200.; self[ 'box' ].box[1][1] = -200.
        self[ 'box' ].box[2][0] =  200.; self[ 'box' ].box[2][1] =  200.
        self[ 'box' ].box[3][0] = -200.; self[ 'box' ].box[3][1] =  200.

    def collides( self, obj ):
        return self['box'].collides( obj )



class Taverna( pyscumm.scene.Scene ):
    def start( self ):
        self._state = Taverna1()

        a=0
        while a < 30:
            x = MyObject()
            x[ 'box' ].location[0] = random.random() * 640
            x[ 'box' ].location[1] = random.random() * 320
            self[ id(x) ] = x
            a=a+1



class Taverna1( pyscumm.scene.SceneState ):
    pass

pyscumm.vm.VM().state = pyscumm.vm.NormalMode()
pyscumm.vm.VM.boot( Taverna() )
