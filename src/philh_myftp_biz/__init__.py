
from .other import *

from . import (
    array,
    classOBJ,
    file,
    modules,
    web,
    pc,
    text,
    time,
    num,
    json
)

# Declare Modules
try:
    PC = modules.Module('PC')
    AD = modules.Module('AD')
    AI = modules.Module('AI')
    Ffmpeg = modules.Module('Ffmpeg')
    Minecraft = modules.Module('Minecraft')
    Package = modules.Module('Package')
    Plex = modules.Module('Plex')
    VMs = modules.Module('VMs')
    Website = modules.Module('Website')
    YouTube = modules.Module('YouTube')
    #NoIP = modules.Module('NoIP')
    #Bios = modules.Module('Bios')
except:
    pass
