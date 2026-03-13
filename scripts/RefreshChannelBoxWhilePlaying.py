# script that play each frame and refresh to let user record updates of channel box for demoreel.

import time

import maya.cmds as cmds


def play_each_frame(pStartFrame, pEndFrame, pWaitTime:float=0.005):
    for frame in range(pStartFrame, pEndFrame + 1):
        cmds.currentTime(frame, edit=True)
        cmds.refresh(force=True)
        time.sleep(pWaitTime)

start_frame = int(cmds.playbackOptions(query=True, minTime=True))
end_frame = int(cmds.playbackOptions(query=True, maxTime=True))

play_each_frame(start_frame, end_frame)
