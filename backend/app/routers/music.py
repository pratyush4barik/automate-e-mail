from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from music_system.player import player, is_paused    
import vlc

router = APIRouter()

@router.post("/toggle")
def toggle():
    global is_paused
    state = player.get_state()
    if state in [
        vlc.State.NothingSpecial,
        vlc.State.Stopped,
        vlc.State.Ended
    ]:
        player.play()
        is_paused = False
        
    elif state == vlc.State.Playing:
        player.pause()
        is_paused = True
        
    elif state == vlc.State.Paused:
        player.pause()
        is_paused = False

    return {
        "playing" : not is_paused
    }

@router.post("/forward")
def forward():
    current = player.get_time()
    player.set_time(current + 5000)
    return {"success": True}

@router.post("/backward")
def backward():
    current = player.get_time()
    player.set_time(current - 5000)
    return {"success": True}

@router.post("/stop")
def stop():
    player.stop()
    return {"success": True}
