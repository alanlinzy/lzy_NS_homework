"""
Escape Room Core
"""
import random, sys

#@
class Trap: 
    def __init__(self, output):
        self.output = output
    def initialTrap(self,output):
        self.TRAP = 0
        self.ROAD = 1
        self.PEOPLE = 2
        self.EXIT = 3
        self.DEAD = 10
        self.LIVE = 11
        self.ESCAPED = 12
        self.maplist=[[0,0,0],
                      [0,0,0],
                      [0,0,0]]
        self.playerPosition = [random.choice([r for r in range(2)]),random.choice([c for c in range(3)])]
        self.exitPosition =[2,1]
        self.playerStatus = self.LIVE
        self.output = output
        
        
    def changeMap(self):
        self.generateMap()
        return self.drawMap()

    def getmap(self):
        return self.maplist
    

    def generateMap(self):
        for r in range(3):
            for c in range(3):
                if r == self.playerPosition[0] and c == self.playerPosition[1]:
                    self.maplist[r][c] = self.PEOPLE
                #self.maplist[r][c] != self.PEOPLE and self.maplist[r][c] != self.EXIT:
                elif r == self.exitPosition[0] and c == self.exitPosition[1]:
                    self.maplist[r][c] = self.EXIT
                else:
                    self.maplist[r][c] =  random.choice([self.TRAP,self.ROAD])

    

    def roomContent(self,content):
        if content == self.TRAP:
            return "X"
        elif content == self.PEOPLE:
            return "*"
        elif content == self.EXIT:
            return "@"
        else:
            return " "
        
    def drawMap(self):
        trapmap = "You are in trap room. If you want to go back, you need to move to EXIT.If you go into TRAP, you will die.\n"
        trapmap += "YOU--*  EXIT--@ TRAP--X\n"
        trapmap += "MOVE INPUT: up, down, left, right, wait.\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[0][0]) + ' | ' + self.roomContent(self.maplist[0][1])+ ' | ' + self.roomContent(self.maplist[0][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[1][0]) + ' | ' + self.roomContent(self.maplist[1][1])+ ' | ' + self.roomContent(self.maplist[1][2])+"\n"
        trapmap += '-----------\n'
        trapmap +=' '+ self.roomContent(self.maplist[2][0]) + ' | ' + self.roomContent(self.maplist[2][1])+ ' | ' + self.roomContent(self.maplist[2][2])+"\n"
        trapmap += '-----------\n'
        return trapmap
    
    def isEscape(self):
        if self.playerPosition[0] == self.exitPosition[0] and self.playerPosition[1] == self.exitPosition[1]:
            self.playerStatus = self.ESCAPED
        elif self.maplist[self.playerPosition[0]][self.playerPosition[1]] == self.TRAP:
            self.playerStatus = self.DEAD
        else:
            pass
    def commandHandler(self,command):
        if command == "up":
            #print(command)
            nextY = self.playerPosition[0] -1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY
            else:
                self.output("Can't go that way")
                
        elif command == "down":
            #print(command)
            nextY = self.playerPosition[0] + 1
            if nextY >= 0 and nextY <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[0] = nextY

            else:
                self.output("Can't go that way")
                
        elif command == "left":
            #print(command)
            nextX = self.playerPosition[1] -1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "right":
            #print(command)
            nextX = self.playerPosition[1] +1
            if nextX >= 0 and nextX <= 2:
                self.maplist[self.playerPosition[0]][self.playerPosition[1]] = self.ROAD
                self.playerPosition[1] = nextX
            else:
                self.output("Can't go that way")
                
        elif command == "wait":
            self.output("Waiting")
        else:
            self.output("what to do?")
        self.isEscape()
        self.output(self.changeMap())
        
    #def output(self,string0):
     #   print(string0)
#@

def create_container_contents(*escape_room_objects):
    return {obj.name: obj for obj in escape_room_objects}
    
def listFormat(object_list):
    l = ["a "+object.name for object in object_list if object["visible"]]
    return ", ".join(l)

class EscapeRoomObject:
    def __init__(self, name, **attributes):
        self.name = name
        self.attributes = attributes
        self.triggers = []
        
    def do_trigger(self, *trigger_args):
        return [event for trigger in self.triggers for event in [trigger(self, *trigger_args)] if event]
        
    def __getitem__(self, object_attribute):
        return self.attributes.get(object_attribute, False)
        
    def __setitem__(self, object_attribute, value):
        self.attributes[object_attribute] = value
        
    def __repr__(self):
        return self.name
        
class EscapeRoomCommandHandler:
    def __init__(self, room, player, output=print,isintrap=False):#@!
        self.room = room
        self.player = player
        self.output = output
        self.isintrap = isintrap
        
    def _run_triggers(self, object, *trigger_args):
        for event in object.do_trigger(*trigger_args):
            self.output(event)
        
    def _cmd_look(self, look_args):
        look_result = None
        if len(look_args) == 0:
            object = self.room
        else:
            object = self.room["container"].get(look_args[-1], self.player["container"].get(look_args[-1], None))
        
        if not object or not object["visible"]:
            look_result = "You don't see that here."
        elif object["container"] != False and look_args and "in" == look_args[0]:
            if not object["open"]:
                look_result = "You can't do that! It's closed!"
            else:
                look_result = "Inside the {} you see: {}".format(object.name, listFormat(object["container"].values()))
        else:
            self._run_triggers(object, "look")
            look_result = object.attributes.get("description","You see nothing special")
        self.output(look_result)
        
    def _cmd_unlock(self, unlock_args):
        unlock_result = None
        if len(unlock_args) == 0:
            unlock_result = "Unlock what?!"
        elif len(unlock_args) == 1:
            unlock_result = "Unlock {} with what?".format(unlock_args[0])
        
        else:
            object = self.room["container"].get(unlock_args[0], None)
            unlock = False
            
            if not object or not object["visible"]:
                unlock_result = "You don't see that here."
            elif not object["keyed"] and not object["keypad"]:
                unlock_result = "You can't unlock that!"
            elif not object["locked"]:
                unlock_result = "It's already unlocked"
            
            elif object["keyed"]:
                unlocker = self.player["container"].get(unlock_args[-1], None)
                if not unlocker:
                    unlock_result = "You don't have a {}".format(unlock_args[-1])                    
                elif unlocker not in object["unlockers"]:
                    unlock_result = "It doesn't unlock."
                else:
                    unlock = True
                    
            elif object["keypad"]:
                # TODO: For later Exercise
                pass
            
            if unlock:
                unlock_result = "You hear a click! It worked!"
                object["locked"] = False
                self._run_triggers(object, "unlock", unlocker)
        self.output(unlock_result)
        
    def _cmd_open(self, open_args):
        """
        Let's demonstrate using some ands instead of ifs"
        """
        if len(open_args) == 0:
            return self.output("Open what?")
        object = self.room["container"].get(open_args[-1], None)
        
        success_result = "You open the {}.".format(object.name)
        open_result = (
            ((not object or not object["visible"]) and "You don't see that.") or
            ((object["open"])                      and "It's already open!") or
            ((object["locked"])                    and "It's locked") or
            ((not object["openable"])              and "You can't open that!") or
                                                       success_result)
        if open_result == success_result:
            object["open"] = True
            self._run_triggers(object, "open")
        self.output(open_result)
#@
    def _cmd_push(self, push_args):

        if len(push_args) == 0:
            return self.output("Push what?")
        object = self.room["container"].get(push_args[-1], None)
        
        success_result = "You push the {}.".format(push_args[-1])
        push_result = (
            ((not object or not object["visible"]) and "You don't see that.") or
            ((not object["pushable"])              and "You can't open that!") or
                                                       success_result)
        if push_result == success_result:
            #startTrap(object["trap"],self.output,self.isintrap)
            object["pushable"] = False
            self.isintrap =True
            self._run_triggers(object, "push")
        #self.output(open_result)
#@
    def _cmd_get(self, get_args):
        if len(get_args) == 0:
            get_result = "Get what?"
        elif self.player["container"].get(get_args[0], None) != None:
            get_result = "You already have that"
        else:
            if len(get_args) > 1:
                container = self.room["container"].get(get_args[-1], None)
            else:
                container = self.room
            object = container["container"] and container["container"].get(get_args[0], None) or None
            
            success_result = "You got it"
            get_result = (
                ((not container or container["container"] == False)and "You can't get something out of that!") or
                ((container["openable"] and not container["open"]) and "It's not open.") or
                ((not object or not object["visible"])             and "You don't see that") or
                ((not object["gettable"])                          and "You can't get that.") or
                                                                   success_result)
            
            if get_result == success_result:
                container["container"].__delitem__(object.name)
                self.player["container"][object.name] = object
                self._run_triggers(object, "get",container)
        self.output(get_result)
        
    def _cmd_inventory(self, inventory_args):
        """
        Use return statements to end function early
        """
        if len(inventory_args) != 0:
            self.output("What?!")
            return
            
        items = ", ".join(["a "+item for item in self.player["container"]])
        self._run_triggers(object, "inventory")
        self.output("You are carrying {}".format(items))
        
    def command(self, command_string):
        # no command
        if command_string.strip == "":
            return self.output("")
            
        command_args = command_string.split(" ")
        function = "_cmd_"+command_args[0]
        
        # unknown command
        if not hasattr(self, function):
            return self.output("You don't know how to do that.")
            
        # execute command dynamically
        getattr(self, function)(command_args[1:])
        self._run_triggers(self.room, "_post_command_", *command_args)
        
def create_room_description(room):
    room_data = {
        "mirror": room["container"]["mirror"].name,
        "clock_time": room["container"]["clock"]["time"]
    }
    return """You are in a locked room. There is only one door
and it is locked. Above the door is a clock that reads {clock_time}.
Across from the door is a large {mirror}. Below the mirror is an old chest.

The room is old and musty and the floor is creaky and warped.""".format(**room_data)

def create_door_description(door):
    description = "The door is strong and highly secured."
    if door["locked"]: description += " The door is locked."
    return description
    
def create_mirror_description(mirror, room):
    description = "You look in the mirror and see yourself."
    if "hairpin" in room["container"]:
        description += ".. wait, there's a hairpin in your hair. Where did that come from?"
    return description
    
def create_chest_description(chest):
    description = "An old chest. It looks worn, but it's still sturdy."
    if chest["locked"]:
        description += " And it appears to be locked."
    elif chest["open"]:
        description += " The chest is open."
    return description
    
def advance_time(room, clock):
    event = None
    clock["time"] = clock["time"] - 1
    if clock["time"] == 0:
        for object in room["container"].values():
            if object["alive"]:
                object["alive"] = False
        event = "Oh no! The clock reaches 0 and a deadly gas fills the room!"
    room["description"] = create_room_description(room)
    return event
                
class EscapeRoomGame:
    def __init__(self, command_handler_class=EscapeRoomCommandHandler, output=print):
        self.room, self.player = None, None
        self.output = output
        self.command_handler_class = command_handler_class
        self.command_handler = None
        self.status = "void"
        self.trap = Trap(self.output)#@
        self.isintrap = False#@
        
    def create_game(self, cheat=False):
        clock =  EscapeRoomObject("clock",  visible=True, time=100)
        mirror = EscapeRoomObject("mirror", visible=True)
        hairpin= EscapeRoomObject("hairpin",visible=False, gettable=True)
        door  =  EscapeRoomObject("door",   visible=True, openable=True, open=False, keyed=True, locked=True, unlockers=[hairpin])
        chest  = EscapeRoomObject("chest",  visible=True, openable=True, open=False, keyed=True, locked=True, unlockers=[hairpin])
        room   = EscapeRoomObject("room",   visible=True)
        player = EscapeRoomObject("player", visible=False, alive=True)
        button = EscapeRoomObject("button", visible=True, pushable=True,trap = self.trap)#@
        
        # setup containers
        player["container"]= {}
        chest["container"] = {}
        room["container"]  = create_container_contents(player, door, clock, mirror, hairpin, chest,button)#@
        
        # set initial descriptions (functions)
        room["description"]    = create_room_description(room)
        door["description"]    = create_door_description(door)
        mirror["description"]  = create_mirror_description(mirror, room)
        chest["description"]   = create_chest_description(chest)

        mirror.triggers.append(lambda obj, cmd, *args: (cmd == "look") and hairpin.__setitem__("visible",True))
        mirror.triggers.append(lambda obj, cmd, *args: (cmd == "look") and mirror.__setitem__("description", create_mirror_description(mirror, room)))
        door.triggers.append(lambda obj, cmd, *args: (cmd == "unlock") and door.__setitem__("description", create_door_description(door)))
        door.triggers.append(lambda obj, cmd, *args: (cmd == "open") and room["container"].__delitem__(player.name))
        room.triggers.append(lambda obj, cmd, *args: (cmd == "_post_command_") and advance_time(room, clock))
        button.triggers.append(lambda obj, cmd, *args: (cmd == "push") and self.startTrap())#@
        
        # TODO, the chest needs some triggers. This is for a later exercise
        
        self.room, self.player = room, player
        self.command_handler = self.command_handler_class(room, player, self.output,self.isintrap)
        self.status = "created"
    #@
    def startTrap(self):
        self.isintrap = True
        self.trap.initialTrap(self.output)
        self.output(self.trap.changeMap())
        
    #@      
    def start(self):
        self.status = "playing"
        self.output("Where are you? You don't know how you got here... Were you kidnapped? Better take a look around")
        
    def command(self, command_string):
        if self.status == "void":
            self.output("The world doesn't exist yet!")
        elif self.status == "created":
            self.output("The game hasn't started yet!")
        elif self.status == "dead":
            self.output("You already died! Sorry!")
        elif self.status == "escaped":
            self.output("You already escaped! The game is over!")
        else:
            print(self.isintrap)
            if self.isintrap == True:#@
                if self.trap.playerStatus == self.trap.ESCAPED:
                    self.output('escaped from the trap!')
                    self.isintrap = False
                elif self.trap.playerStatus == self.trap.DEAD:
                    self.output('you die in the trap!')
                    self.isintrap = False
                    self.status = "dead"
                else:
                    self.trap.commandHandler(command_string)
                    
            else:
                self.command_handler.command(command_string)
                if not self.player["alive"]:
                    self.output("You died. Game over!")
                    self.status = "dead"
                elif self.player.name not in self.room["container"]:
                    self.status = "escaped"
                    self.output("VICTORY! You escaped!")#@
        
def main(args):
    game = EscapeRoomGame()
    game.create_game(cheat=("--cheat" in args))
    game.start()
    while game.status == "playing":
        command = input(">> ")
        output = game.command(command)
        
if __name__=="__main__":
    main(sys.argv[1:])
