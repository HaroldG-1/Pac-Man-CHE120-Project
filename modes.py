from constants import *


###########################
# Main Ghost Mode Controller
###########################
class MainMode(object):
    def __init__(self):
        self.timer = 0
        self.scatter()  # Start game in scatter mode (like original Pac-Man)

    # Update timing and check whether mode should switch
    def update(self, dt):
        self.timer += dt
        
        # If time for the current mode runs out, switch mode
        if self.timer >= self.time:
            if self.mode is SCATTER:
                self.chase()
            elif self.mode is CHASE:
                self.scatter()

    # Switch to SCATTER mode
    def scatter(self):
        self.mode = SCATTER
        self.time = 7       # SCATTER mode lasts 7 seconds
        self.timer = 0

    # Switch to CHASE mode
    def chase(self):
        self.mode = CHASE
        self.time = 20      # CHASE mode lasts 20 seconds
        self.timer = 0


###########################
# Mode Controller
###########################
class ModeController(object):
    def __init__(self, entity):
        self.timer = 0
        self.time = None
        
        # Controls standard chase/scatter timing
        self.mainmode = MainMode()
        
        # Track current behavior mode
        self.current = self.mainmode.mode
        
        # Reference to ghost
        self.entity = entity 

    # Update ghost behavior mode
    def update(self, dt):
        self.mainmode.update(dt)

        #############################
        # FREIGHT (ghost scared mode)
        #############################
        if self.current is FREIGHT:
            self.timer += dt
            
            # When freight time ends, ghost returns to normal mode
            if self.timer >= self.time:
                self.time = None
                self.entity.normalMode()
                self.current = self.mainmode.mode

        #############################
        # Sync ghost mode with MainMode (SCATTER / CHASE)
        #############################
        elif self.current in [SCATTER, CHASE]:
            self.current = self.mainmode.mode

        #############################
        # SPAWN (ghost returning to center after being eaten)
        #############################
        if self.current is SPAWN:
            # When ghost reaches spawn node, return to normal behavior
            if self.entity.node == self.entity.spawnNode:
                self.entity.normalMode()
                self.current = self.mainmode.mode

    # Set mode to SPAWN only if currently in FREIGHT
    def setSpawnMode(self):
        if self.current is FREIGHT:
            self.current = SPAWN

    # Trigger FREIGHT mode (ghost-blue mode)
    def setFreightMode(self):
        # If ghost is in normal mode, activate freight mode
        if self.current in [SCATTER, CHASE]:
            self.timer = 0
            self.time = 7   # Duration ghosts stay frightened
            self.current = FREIGHT
        
        # If already in freight, restart timer (stack effect)
        elif self.current is FREIGHT:
            self.timer = 0
