from utils import *
import pygame,time,threading
class NoJoystickException(Exception):
	def __init__(self,raison):
		self.raison = raison
    
	def __str__(self):
		return self.raison

class Joystick(threading.Thread):
	x=0
	y=0
	z=0
	v=0	
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		pygame.init()
		#pygame.display.init()  
		pygame.joystick.init()   
		if not pygame.joystick.get_count():  
			raise NoJoystickException("Please connect a joystick and run again.")
		self.j = pygame.joystick.Joystick(0)
		self.j.init()
		self.start()
		info("%d joystick(s) detected, %s will be used to control Grbl." % (pygame.joystick.get_count(),self.j.get_name()))

	
	def _handleJoyEvent(self,e):  
		global data,ser
		if e.type == pygame.JOYAXISMOTION:   
			if (e.dict['axis'] == 0):  
				self.x=e.dict['value']
			if (e.dict['axis'] == 1):  
				self.y=e.dict['value']*-1 #Invert Y axis to natural direction
			if (e.dict['axis'] == 2):  
				self.z=e.dict['value']
			if (e.dict['axis'] == 3):  
				self.v=e.dict['value']
		else:  
			pass  

	def run(self):
		while(True):
			events = pygame.event.get()
			for e in events :
				if (not e == pygame.NOEVENT and (e.type == pygame.JOYAXISMOTION or e.type == pygame.JOYBUTTONDOWN  or e.type == pygame.JOYBUTTONUP)):  
					self._handleJoyEvent(e)
			time.sleep(0.005)


	def getAxisValues(self):
		return(self.x,self.y,self.z,self.v)
		

if __name__ == "__main__":
	try:
		joystick = Joystick()
		while(True):
			print joystick.getAxisValues()
			time.sleep(1)
	except NoJoystickException, e:
		print(e)
	except KeyboardInterrupt, e:
		exit(0)
